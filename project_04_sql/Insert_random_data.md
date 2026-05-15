## Insert random data to order table
```plantuml
INSERT INTO orders (
    order_date, seller_id, status, total_amount, created_at
)
select *, 
order_date + interval '1 day' AS created_at
FROM 
(
	SELECT
		random() * 
       (timestamp '2025-10-31 23:59:59' - timestamp '2025-08-01 00:00:00') + 
       timestamp '2025-08-01 00:00:00',
		random(1, 5) as seller_id,
		('{PLACED,PAID,SHIPPED,DELIVERED,CANCELLED,RETURNED}'::text[])[ceil(random()*6)] AS status,
		random(1, 100) as total_amount
	from generate_series(1, 3000000) s(i)
) main ;
```

## Insert random data to order_items table
```plantuml
INSERT INTO order_items(
	order_id,product_id,order_date,quantity,unit_price,subtotal,created_at
)
WITH RECURSIVE order_distribution AS (
    -- Step 1: Get all orders
    SELECT 
        o.order_id,
        o.total_amount,
        o.order_date
    FROM orders o
    -- Only process orders that don't have items yet
    WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.order_id = o.order_id)
),
item_rows AS (
    -- 2. Generate the actual number of rows needed
    SELECT 
        order_id,
        total_amount,
        order_date,
        row_number() OVER (ORDER BY order_id, random()) as global_item_id
    FROM order_distribution
    CROSS JOIN LATERAL generate_series(1, total_amount)
),
shuffled_products AS (
    -- Step 3: randomized list of all products with an index
    SELECT 
        product_id,
		price,
        row_number() OVER (ORDER BY random()) as product_row_id
    FROM products
),
final_item AS (
    -- Step 4 finalize products random and quantity by order_id and product_id 
    SELECT 
        it.order_id,
        it.total_amount,
        it.order_date,
		sp.product_id,
		sp.price,
		count(*) OVER(PARTITION BY it.order_id, sp.product_id) AS quantity
    FROM item_rows it
	JOIN shuffled_products sp ON sp.product_row_id = 
        ((it.global_item_id  % (SELECT count(*) FROM products)) + 1)	
)
-- Step 5: Final Insert 
SELECT 
    order_id,
    product_id,
	order_date,
	--total_amount,
	quantity,
	price,
	quantity * price AS subtotal,
	order_date + interval '2 hour' AS created_at
FROM final_item;
```