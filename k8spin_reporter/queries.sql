-- SQLite

-- CONSUMO ACTUAL POR SPACE

    SELECT t2.organization_id, t2.tenant_id, t2.space_id, t2.cpu, t2.memory FROM (

        SELECT organization_id as org, tenant_id, space_id, max(id) id
        FROM space_usage
        GROUP BY organization_id, tenant_id, space_id
    ) t1, space_usage t2 WHERE
    t1.id = t2.id;


-- CONSUMO ACTUAL POR TENANT

    SELECT t2.organization_id, t2.tenant_id, sum(t2.cpu), sum(t2.memory) FROM (

        SELECT organization_id as org, tenant_id, space_id, max(id) id
        FROM space_usage
        GROUP BY organization_id, tenant_id, space_id
    ) t1, space_usage t2 WHERE
    t1.id = t2.id
    GROUP BY t2.organization_id, t2.tenant_id;


-- CONSUMO ACTUAL POR ORGANIZATION

    SELECT t2.organization_id, sum(t2.cpu), sum(t2.memory) FROM (

        SELECT organization_id as org, tenant_id, space_id, max(id) id
        FROM space_usage
        GROUP BY organization_id, tenant_id, space_id
    ) t1, space_usage t2 WHERE
    t1.id = t2.id
    GROUP BY t2.organization_id;

-- CONSUMO ACTUAL POR ORGANIZATION

SELECT t1.organization_id, t1.allocated_cpu, t1.allocated_memory, t2.used_cpu, t2.used_memory
FROM 
(
    SELECT t2.organization_id as organization_id, t2.cpu as allocated_cpu, t2.memory as allocated_memory FROM
    (
        SELECT cpu,memory, max(id) id
        FROM organization_resources
        GROUP BY organization_id
    ) t1, organization_resources t2
    WHERE t1.id = t2.id
) t1,
(
    SELECT t2.organization_id as organization_id, sum(t2.cpu) as used_cpu, sum(t2.memory) as used_memory FROM
    (
        SELECT organization_id, tenant_id, space_id, max(id) id
        FROM space_usage
        GROUP BY organization_id, tenant_id, space_id
    )
    t1, space_usage t2
    WHERE t1.id = t2.id
    GROUP BY t2.organization_id
) t2
WHERE t1.organization_id = t2.organization_id;


---

-- Recursos usados de media en los spaces. Diario

SELECT organization_id, tenant_id, space_id, strftime('%Y%m%d', reported) as day, avg(cpu) as cpu, avg(memory) as memory
FROM space_usage
WHERE organization_id = "d831bb55-b4fd-4971-8230-4fdd0141d3b2"
GROUP BY organization_id, tenant_id, space_id, strftime('%Y%m%d', reported)
ORDER BY strftime('%Y%m%d', reported) DESC;

-- Recursos usados de media en los spaces, sumados para saber a nivel de organizacion. Diario

SELECT organization_id, day, sum(cpu), sum(memory)
FROM (

    SELECT organization_id, tenant_id, space_id, strftime('%Y%m%d', reported) as day, avg(cpu) as cpu, avg(memory) as memory
    FROM space_usage
    WHERE organization_id = "d831bb55-b4fd-4971-8230-4fdd0141d3b2"
    GROUP BY organization_id, tenant_id, space_id, strftime('%Y%m%d', reported)

)
GROUP BY organization_id, day
ORDER BY day DESC;


-- Recursos reservados en una organizacion de media por dia

SELECT organization_id, strftime('%Y%m%d', reported) as day, avg(cpu) as cpu, avg(memory) as memory
FROM organization_resources
WHERE organization_id = "d831bb55-b4fd-4971-8230-4fdd0141d3b2"
GROUP BY organization_id, strftime('%Y%m%d', reported)



-- Datos de una organizacion diarios, allocated y usados

SELECT used.day, allocated.allocated_cpu, used.used_cpu, allocated.allocated_memory, used.used_memory

FROM (

    SELECT organization_id, day, sum(cpu) as used_cpu, sum(memory) as used_memory
    FROM (
        SELECT organization_id, tenant_id, space_id, strftime('%Y%m%d', reported) as day, avg(cpu) as cpu, avg(memory) as memory
        FROM space_usage
        WHERE organization_id = "d831bb55-b4fd-4971-8230-4fdd0141d3b2"
        GROUP BY organization_id, tenant_id, space_id, strftime('%Y%m%d', reported)
    )
    GROUP BY organization_id, day

) used, 

(
    SELECT organization_id, strftime('%Y%m%d', reported) as day, avg(cpu) as allocated_cpu, avg(memory) as allocated_memory
    FROM organization_resources
    WHERE organization_id = "d831bb55-b4fd-4971-8230-4fdd0141d3b2"
    GROUP BY organization_id, strftime('%Y%m%d', reported)

) allocated

WHERE used.organization_id = "d831bb55-b4fd-4971-8230-4fdd0141d3b2"
AND used.organization_id = allocated.organization_id
AND used.day = allocated.day
ORDER BY used.day DESC
LIMIT 7;



---

-- Datos de una organizacion de las ultimas 24h, allocated y usados

SELECT used.day, allocated.allocated_cpu, used.used_cpu, allocated.allocated_memory, used.used_memory

FROM (

    SELECT organization_id, day, sum(cpu) as used_cpu, sum(memory) as used_memory
    FROM (
        SELECT organization_id, tenant_id, space_id, strftime('%Y%m%d%H', reported) as day, avg(cpu) as cpu, avg(memory) as memory
        FROM space_usage
        WHERE organization_id = "d831bb55-b4fd-4971-8230-4fdd0141d3b2"
        GROUP BY organization_id, tenant_id, space_id, strftime('%Y%m%d%H', reported)
    )
    GROUP BY organization_id, day

) used, 

(
    SELECT organization_id, strftime('%Y%m%d%H', reported) as day, avg(cpu) as allocated_cpu, avg(memory) as allocated_memory
    FROM organization_resources
    WHERE organization_id = "d831bb55-b4fd-4971-8230-4fdd0141d3b2"
    GROUP BY organization_id, strftime('%Y%m%d%H', reported)

) allocated

WHERE used.organization_id = "d831bb55-b4fd-4971-8230-4fdd0141d3b2"
AND used.organization_id = allocated.organization_id
AND used.day = allocated.day
ORDER BY used.day DESC
LIMIT 24;








-- SELECT t2.organization_id as organization_id, t2.cpu as allocated_cpu, t2.memory as allocated_memory FROM
-- (
--     SELECT cpu,memory, max(id) id
--     FROM organization_resources
--     GROUP BY organization_id
-- ) t1, organization_resources t2
-- WHERE t1.id = t2.id;



--     SELECT t2.organization_id, sum(t2.cpu), sum(t2.memory) FROM (

--         SELECT organization_id as org, tenant_id, space_id, max(id) id
--         FROM space_usage
--         GROUP BY organization_id, tenant_id, space_id
--     ) t1, space_usage t2, (
    
--         SELECT cpu,memory, max(id) id
--             FROM organization_resources
--             GROUP BY organization_id
    
--     ) t3,  organization_resources t4 WHERE
--     t1.id = t2.id AND t3.id = t4.id
--     AND t2.organization_id = t4.organization_id
--     GROUP BY t2.organization_id;


--         SELECT id, name from organization;



-- WHERE organization_id = "d831bb55-b4fd-4971-8230-4fdd0141d3b2"