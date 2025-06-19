import re

def limpia_lineas(sql):
    # Elimina líneas completamente comentadas y comentarios de línea
    lineas = []
    for linea in sql.splitlines():
        l = linea.strip()
        if l.startswith('--'):
            continue
        # Elimina comentarios en línea
        if '--' in l:
            l = l.split('--', 1)[0].strip()
        if l:
            lineas.append(l)
    return '\n'.join(lineas)

def extrae_tablas_fuente(sql, fuente):
    # Busca tablas después de FROM o JOIN (fuente)
    return re.findall(rf'\b{fuente}\s+([A-Z0-9_.]+)', sql, re.IGNORECASE)

def extrae_tablas_select(sql):
    # Busca tablas en subconsultas del SELECT
    tablas = []
    # Subselects tipo (SELECT ... FROM tabla ...)
    for match in re.finditer(r'\(\s*SELECT.*?FROM\s+([A-Z0-9_.]+)', sql, re.IGNORECASE | re.DOTALL):
        tablas.append(match.group(1))
    return tablas

def extrae_tablas_where(sql):
    # Busca posibles referencias a tablas en el WHERE (esquema.tabla.columna)
    return re.findall(r'([A-Z0-9_]+\.[A-Z0-9_]+)\.', sql, re.IGNORECASE)

def main():
    with open('entrada.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    sql_limpio = limpia_lineas(sql)

    tablas_from = extrae_tablas_fuente(sql_limpio, 'FROM')
    tablas_join = extrae_tablas_fuente(sql_limpio, 'JOIN')
    tablas_select = extrae_tablas_select(sql_limpio)
    tablas_where = extrae_tablas_where(sql_limpio)

    # Unifica FROM y JOIN, elimina duplicados y ordena
    tablas_fuente = sorted(set(tablas_from + tablas_join))
    tablas_select = sorted(set(tablas_select) - set(tablas_fuente))
    tablas_where = sorted(set(tablas_where) - set(tablas_fuente) - set(tablas_select))

    # Genera el SQL de salida
    salida = []
    if tablas_fuente:
        #salida.append('-- Tablas encontradas en FROM/JOIN')
        for t in tablas_fuente:
            salida.append(t)
        salida.append('')

    if tablas_select:
        #salida.append('-- Tablas encontradas en SELECT (subconsultas)')
        for t in tablas_select:
            salida.append(t)
        salida.append('')

    if tablas_where:
        #salida.append('-- Tablas encontradas en WHERE')
        for t in tablas_where:
            salida.append(t)
        salida.append('')

    # Escribe el resultado en tablas.sql
    with open('tablas.sql', 'w', encoding='utf-8') as f:
        f.write('\n'.join(salida))
    print('🟢 Tablas extraídas y guardadas en tablas.sql')

if __name__ == '__main__':
    main()