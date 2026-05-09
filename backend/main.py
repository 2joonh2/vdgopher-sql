from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlglot
from sqlglot.optimizer.qualify import qualify
from sqlglot.optimizer.scope import build_scope, Scope
from typing import List, Dict, Any, Optional, Set
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SQLRequest(BaseModel):
    sql: str
    dialect: Optional[str] = None

def build_lineage_graph(sql: str, dialect: str = None):
    try:
        nodes = []
        edges = []
        node_ids = set()
        column_node_map = {}

        def add_group_node(table_name: str):
            clean_name = table_name.replace('"', '').replace('`', '').upper()
            group_id = f"group_{clean_name.lower()}"
            if group_id not in node_ids:
                nodes.append({
                    "id": group_id,
                    "type": "group",
                    "data": {"label": clean_name, "type": "table_group"},
                    "style": { "zIndex": -1 },
                    "position": {"x": 0, "y": 0}
                })
                node_ids.add(group_id)
            return group_id

        def get_or_create_node(table_name: str, col_name: str, node_type: str, agg_info: str = ""):
            t_name = table_name.replace('"', '').replace('`', '').upper() if table_name else "RESULT"
            c_name = col_name.replace('"', '').replace('`', '').upper()
            
            clean_table = t_name.lower()
            clean_col = c_name.lower()
            key = (clean_table, clean_col)
            
            if key in column_node_map:
                node_id = column_node_map[key]
                for node in nodes:
                    if node["id"] == node_id:
                        if agg_info and agg_info not in node["data"]["label"]:
                            node["data"]["label"] = f"{node['data']['label']} {agg_info}".strip()
                        
                        type_priority = {"join_key": 10, "final_column": 5, "source_column": 3, "data_source": 1}
                        current_type = node.get("type", "source_column")
                        if type_priority.get(node_type, 0) > type_priority.get(current_type, 0):
                            node["type"] = node_type
                            node["data"]["type"] = node_type
                return node_id
            
            node_id = str(uuid.uuid4())
            group_id = add_group_node(t_name)
            
            nodes.append({
                "id": node_id,
                "type": node_type,
                "data": {
                    "label": f"{c_name} {agg_info}".strip(), 
                    "type": node_type,
                    "table": t_name
                },
                "parentNode": group_id,
                "extent": "parent",
                "position": {"x": 20, "y": 60}
            })
            column_node_map[key] = node_id
            node_ids.add(node_id)
            return node_id

        def add_edge(source_id: str, target_id: str):
            if not source_id or not target_id or source_id == target_id: return
            edge_id = f"e-{source_id}-{target_id}"
            if not any(e["id"] == edge_id for e in edges):
                edges.append({
                    "id": edge_id,
                    "source": source_id,
                    "target": target_id,
                    "animated": True,
                    "style": {"zIndex": 5}
                })

        expressions = sqlglot.parse(sql, read=dialect)
        if not expressions:
            raise ValueError("Could not parse any SQL expressions.")

        global_join_keys = set()
        for expr in expressions:
            for join in expr.find_all(sqlglot.exp.Join):
                on_clause = join.args.get("on")
                if on_clause and isinstance(on_clause, sqlglot.exp.EQ):
                    if hasattr(on_clause.left, 'name'): global_join_keys.add(on_clause.left.name.lower())
                    if hasattr(on_clause.right, 'name'): global_join_keys.add(on_clause.right.name.lower())

        processed_scopes = set()

        def process_scope(scope: Scope):
            if not scope or scope in processed_scopes: return
            processed_scopes.add(scope)

            # 1. 하위 스코프들 처리 (재귀)
            for _, source in scope.sources.items():
                if isinstance(source, Scope):
                    process_scope(source)

            # 2. 명칭 결정
            if hasattr(scope.expression, 'parent') and hasattr(scope.expression.parent, 'alias'):
                scope_name = scope.expression.parent.alias
            elif scope.expression == main_expr:
                scope_name = "RESULT"
            else:
                scope_name = "SUBQUERY"

            # 3. 출력 노드 생성 및 "직계 부모"와만 연결
            if isinstance(scope.expression, sqlglot.exp.Select):
                for exp in scope.expression.expressions:
                    alias = exp.alias if isinstance(exp, sqlglot.exp.Alias) else exp.name
                    if not alias: continue
                    
                    node_id = get_or_create_node(scope_name, alias, "final_column" if scope_name == "RESULT" else "source_column")
                    
                    # [핵심 수정] 재귀적 탐색이 아닌 현재 표현식의 직계 컬럼 참조만 추출
                    # find_all(Column)은 모든 깊이를 탐색하므로, 
                    # 하위 테이블의 별칭(t1.status)이 있는지 확인하여 해당 스코프의 직접 소스만 필터링
                    for column in exp.find_all(sqlglot.exp.Column):
                        source_alias = column.table
                        actual_source = scope.sources.get(source_alias)
                        
                        if actual_source:
                            source_table_name = ""
                            if isinstance(actual_source, Scope):
                                source_table_name = actual_source.expression.parent.alias if hasattr(actual_source.expression.parent, 'alias') else "SUBQUERY"
                            elif isinstance(actual_source, sqlglot.exp.Table):
                                source_table_name = actual_source.name
                            
                            if source_table_name:
                                src_id = get_or_create_node(source_table_name, column.name, "data_source")
                                add_edge(src_id, node_id)

            elif isinstance(scope.expression, (sqlglot.exp.Union, sqlglot.exp.Except, sqlglot.exp.Intersect)):
                # UNION 구문: 여러 분기(Selects)의 결과를 현재 스코프로 수집
                first_select = scope.expression.find(sqlglot.exp.Select)
                if not first_select: return
                
                # 출력 노드 목록 생성 (인덱스 기반 매핑용)
                output_ids = []
                for exp in first_select.expressions:
                    alias = exp.alias if isinstance(exp, sqlglot.exp.Alias) else exp.name
                    if not alias: continue
                    node_id = get_or_create_node(scope_name, alias, "source_column")
                    output_ids.append(node_id)
                
                # [핵심 수정] UNION의 각 분기(Select)를 직계 부모로 취급하여 연결
                # scope.sources에는 Union에 참여하는 하위 스코프들이 담겨 있음
                for _, source_scope in scope.sources.items():
                    if isinstance(source_scope, Scope):
                        source_select = source_scope.expression if isinstance(source_scope.expression, sqlglot.exp.Select) else source_scope.expression.find(sqlglot.exp.Select)
                        if not source_select: continue
                        
                        source_table = source_scope.expression.parent.alias if hasattr(source_scope.expression.parent, 'alias') else "SUBQUERY"
                        
                        for idx, s_exp in enumerate(source_select.expressions):
                            s_alias = s_exp.alias if isinstance(s_exp, sqlglot.exp.Alias) else s_exp.name
                            if s_alias and idx < len(output_ids):
                                src_id = get_or_create_node(source_table, s_alias, "source_column")
                                add_edge(src_id, output_ids[idx])

            # 4. 조인 수렴 처리 (중간 단계 건너뛰기 방지)
            for join in scope.expression.find_all(sqlglot.exp.Join):
                on_clause = join.args.get("on")
                if on_clause and isinstance(on_clause, sqlglot.exp.EQ):
                    l, r = on_clause.left, on_clause.right
                    if isinstance(l, sqlglot.exp.Column) and isinstance(r, sqlglot.exp.Column):
                        l_src, r_src = scope.sources.get(l.table), scope.sources.get(r.table)
                        if l_src and r_src:
                            l_name = l_src.name if isinstance(l_src, sqlglot.exp.Table) else "SUBQUERY"
                            r_name = r_src.name if isinstance(r_src, sqlglot.exp.Table) else "SUBQUERY"
                            # 조인 키 노드 참조
                            id_l = get_or_create_node(l_name, l.name, "join_key")
                            id_r = get_or_create_node(r_name, r.name, "join_key")
                            # 현재 스코프의 출력 컬럼 중 이 조인 키와 이름이 같은 것을 찾아 연결
                            # (이것이 해당 단계에서의 '수렴' 포인트임)
                            pass # 위 Select 처리 로직에서 컬럼 참조를 통해 이미 처리됨

        for main_expr in expressions:
            if isinstance(main_expr, (sqlglot.exp.Select, sqlglot.exp.Union)):
                try: qualified = qualify(main_expr, dialect=dialect, validate_qualify_columns=False)
                except Exception: qualified = main_expr
                root_scope = build_scope(qualified)
                if root_scope: process_scope(root_scope)

        return {"nodes": nodes, "edges": edges}
    except Exception as e:
        print(f"General Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/parse")
async def parse_sql(request: SQLRequest):
    return build_lineage_graph(request.sql, request.dialect)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
