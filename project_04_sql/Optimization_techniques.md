# Before Optimize
### 1. Total revenue per month
```plantuml
EXPLAIN SELECT 
    date_trunc('month',oi.order_date) AS order_month, 
    SUM(oi.subtotal) AS total_revenue
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
WHERE o.status NOT IN ('PLACED','RETURNED', 'CANCELLED')
GROUP BY 1
ORDER BY 1;
```
**=> Result:**
```plantuml
"Finalize GroupAggregate  (cost=5575244.87..5594800.52 rows=62574 width=40)"
"  Group Key: (date_trunc('month'::text, oi.order_date))"
"  ->  Gather Merge  (cost=5575244.87..5592735.57 rows=150178 width=40)"
"        Workers Planned: 2"
"        ->  Sort  (cost=5574244.85..5574401.28 rows=62574 width=40)"
"              Sort Key: (date_trunc('month'::text, oi.order_date))"
"              ->  Partial HashAggregate  (cost=5259700.03..5569259.80 rows=62574 width=40)"
"                    Group Key: date_trunc('month'::text, oi.order_date)"
"                    Planned Partitions: 4"
"                    ->  Parallel Hash Join  (cost=54486.34..3235145.21 rows=31602807 width=16)"
"                          Hash Cond: (oi.order_id = o.order_id)"
"                          ->  Parallel Seq Scan on order_items_old oi  (cost=0.00..2193566.67 rows=63138267 width=20)"
"                          ->  Parallel Hash  (cost=44220.50..44220.50 rows=625667 width=4)"
"                                ->  Parallel Seq Scan on orders_old o  (cost=0.00..44220.50 rows=625667 width=4)"
"                                      Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"JIT:"
"  Functions: 16"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 3 | Query complete 00:07:57.127**


### 2. Orders filtered by seller and date
```plantuml
EXPLAIN SELECT order_id,
	order_date,
	seller_id,
	row_number() OVER (ORDER BY date_trunc('day',order_date), seller_id) AS order_by
FROM orders;
```
**=> Results:**
```plantuml
"WindowAgg  (cost=537175.36..604649.60 rows=2998856 width=32)"
"  Window: w1 AS (ORDER BY (date_trunc('day'::text, order_date)), seller_id ROWS UNBOUNDED PRECEDING)"
"  ->  Sort  (cost=537175.34..544672.48 rows=2998856 width=24)"
"        Sort Key: (date_trunc('day'::text, order_date)), seller_id"
"        ->  Seq Scan on orders  (cost=0.00..91554.70 rows=2998856 width=24)"
"JIT:"
"  Functions: 5"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 3000000 | Query complete 00:00:08.916**


### 3. Filter data in order_item by product_id
```plantuml
EXPLAIN SELECT order_id,
	order_item_id,
	product_id
FROM order_items
ORDER BY 3;
```
**=> Results:**
```plantuml
"Sort  (cost=1530097.70..1552599.52 rows=9000727 width=12)"
"  Sort Key: product_id"
"  ->  Seq Scan on order_items  (cost=0.00..182798.27 rows=9000727 width=12)"
"JIT:"
"  Functions: 2"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 9000674 | Query complete 00:00:15.454**


### 4. Find order with highest total_amount
```plantuml
EXPLAIN SELECT oi.order_id,
	SUM(oi.subtotal)
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status NOT IN ('PLACED','RETURNED', 'CANCELLED')
GROUP BY oi.order_id
ORDER BY 2;
```
**=> Results:**
```plantuml
"Sort  (cost=5397149.67..5397306.11 rows=62574 width=36)"
"  Sort Key: (sum(oi.subtotal))"
"  ->  Finalize GroupAggregate  (cost=5372765.42..5392164.63 rows=62574 width=36)"
"        Group Key: oi.order_id"
"        ->  Gather Merge  (cost=5372765.42..5390256.12 rows=150178 width=36)"
"              Workers Planned: 2"
"              ->  Sort  (cost=5371765.39..5371921.83 rows=62574 width=36)"
"                    Sort Key: oi.order_id"
"                    ->  Partial HashAggregate  (cost=5057377.01..5366780.35 rows=62574 width=36)"
"                          Group Key: oi.order_id"
"                          Planned Partitions: 4"
"                          ->  Parallel Hash Join  (cost=54486.34..3032822.19 rows=31602807 width=12)"
"                                Hash Cond: (oi.order_id = o.order_id)"
"                                ->  Parallel Seq Scan on order_items_old oi  (cost=0.00..2193566.67 rows=63138267 width=12)"
"                                ->  Parallel Hash  (cost=44220.50..44220.50 rows=625667 width=4)"
"                                      ->  Parallel Seq Scan on orders_old o  (cost=0.00..44220.50 rows=625667 width=4)"
"                                            Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"JIT:"
"  Functions: 16"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 2000935 | Query complete 00:01:19.291**

### 5. List products with highest quantity sold
```plantuml
EXPLAIN SELECT oi.product_id,
	p.product_name,
	SUM(oi.subtotal) 
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.status NOT IN ('PLACED','RETURNED', 'CANCELLED')
GROUP BY oi.product_id, p.product_name
ORDER BY 3 DESC;
```
**=> Results:**
```plantuml
"Sort  (cost=7088457.51..7090795.01 rows=935000 width=63)"
"  Sort Key: (sum(oi.subtotal)) DESC"
"  ->  Finalize GroupAggregate  (cost=6629944.44..6925422.72 rows=935000 width=63)"
"        Group Key: oi.product_id, p.product_name"
"        ->  Gather Merge  (cost=6629944.44..6891295.22 rows=2244000 width=63)"
"              Workers Planned: 2"
"              ->  Sort  (cost=6628944.42..6631281.92 rows=935000 width=63)"
"                    Sort Key: oi.product_id, p.product_name"
"                    ->  Partial HashAggregate  (cost=5960428.27..6465909.63 rows=935000 width=63)"
"                          Group Key: oi.product_id, p.product_name"
"                          Planned Partitions: 64"
"                          ->  Hash Join  (cost=54530.84..3116175.64 rows=31602807 width=39)"
"                                Hash Cond: (oi.product_id = p.product_id)"
"                                ->  Parallel Hash Join  (cost=54486.34..3032822.19 rows=31602807 width=12)"
"                                      Hash Cond: (oi.order_id = o.order_id)"
"                                      ->  Parallel Seq Scan on order_items_old oi  (cost=0.00..2193566.67 rows=63138267 width=16)"
"                                      ->  Parallel Hash  (cost=44220.50..44220.50 rows=625667 width=4)"
"                                            ->  Parallel Seq Scan on orders_old o  (cost=0.00..44220.50 rows=625667 width=4)"
"                                                  Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                ->  Hash  (cost=32.00..32.00 rows=1000 width=31)"
"                                      ->  Seq Scan on products p  (cost=0.00..32.00 rows=1000 width=31)"
"JIT:"
"  Functions: 24"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 1000 | Query complete 00:00:57.308**


### 6. Orders by Seller in October
```plantuml
EXPLAIN SELECT 
	s.seller_name,
	date_trunc('month',oi.order_date) AS order_month,
	count(o.seller_id)
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN sellers s ON s.seller_id = o.seller_id
WHERE EXTRACT(MONTH FROM oi.order_date) = 10
GROUP BY 1,2
ORDER BY 3
```
**=> Result:**
```plantuml
"Sort  (cost=247165.63..247278.14 rows=45004 width=334)"
"  Sort Key: (count(o.seller_id))"
"  ->  GroupAggregate  (cost=230622.78..236764.32 rows=45004 width=334)"
"        Group Key: s.seller_name, (date_trunc('month'::text, oi.order_date))"
"        ->  Gather Merge  (cost=230622.78..235864.24 rows=45004 width=330)"
"              Workers Planned: 2"
"              ->  Sort  (cost=229622.76..229669.64 rows=18752 width=330)"
"                    Sort Key: s.seller_name, (date_trunc('month'::text, oi.order_date))"
"                    ->  Hash Join  (cost=149292.87..225404.36 rows=18752 width=330)"
"                          Hash Cond: (o.seller_id = s.seller_id)"
"                          ->  Parallel Hash Join  (cost=149279.94..225293.73 rows=18752 width=12)"
"                                Hash Cond: (o.order_id = oi.order_id)"
"                                ->  Parallel Seq Scan on orders o  (cost=0.00..66564.23 rows=1249523 width=8)"
"                                ->  Parallel Hash  (cost=149045.54..149045.54 rows=18752 width=12)"
"                                      ->  Parallel Seq Scan on order_items oi  (cost=0.00..149045.54 rows=18752 width=12)"
"                                            Filter: (EXTRACT(month FROM order_date) = '10'::numeric)"
"                          ->  Hash  (cost=11.30..11.30 rows=130 width=322)"
"                                ->  Seq Scan on sellers s  (cost=0.00..11.30 rows=130 width=322)"
"JIT:"
"  Functions: 24"
"  Options: Inlining false, Optimization false, Expressions true, Deforming true"
```
**Total rows: 25 | Query complete 00:01:55.994**

### 7. Revenue per Product per Month
```plantuml
EXPLAIN SELECT 
	p.product_name,
    date_trunc('month',oi.order_date) AS order_month, 
    SUM(oi.subtotal) AS total_revenue
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.status NOT IN ('PLACED','RETURNED', 'CANCELLED')
GROUP BY p.product_name, order_month
ORDER BY 3;
```
**=> Result:**
```plantuml
"Sort  (cost=35199772.26..35346038.98 rows=58506690 width=67)"
"  Sort Key: (sum(oi.subtotal))"
"  ->  GroupAggregate  (cost=10172669.14..20452722.44 rows=58506690 width=67)"
"        Group Key: p.product_name, (date_trunc('month'::text, oi.order_date))"
"        ->  Gather Merge  (cost=10172669.14..19006271.56 rows=75846737 width=43)"
"              Workers Planned: 2"
"              ->  Sort  (cost=10171669.12..10250676.14 rows=31602807 width=43)"
"                    Sort Key: p.product_name, (date_trunc('month'::text, oi.order_date))"
"                    ->  Hash Join  (cost=54530.84..3318498.66 rows=31602807 width=43)"
"                          Hash Cond: (oi.product_id = p.product_id)"
"                          ->  Parallel Hash Join  (cost=54486.34..3156138.19 rows=31602807 width=20)"
"                                Hash Cond: (oi.order_id = o.order_id)"
"                                ->  Parallel Seq Scan on order_items_old oi  (cost=0.00..2193566.67 rows=63138267 width=24)"
"                                ->  Parallel Hash  (cost=44220.50..44220.50 rows=625667 width=4)"
"                                      ->  Parallel Seq Scan on orders_old o  (cost=0.00..44220.50 rows=625667 width=4)"
"                                            Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                          ->  Hash  (cost=32.00..32.00 rows=1000 width=31)"
"                                ->  Seq Scan on products p  (cost=0.00..32.00 rows=1000 width=31)"
"JIT:"
"  Functions: 22"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 2805 | Query complete 00:05:46.368**

### 8. Products Sold per Seller
```plantuml
EXPLAIN SELECT 
	s.seller_id,
	COUNT(oi.product_id) AS total_products_sold
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN sellers s ON s.seller_id = o.seller_id
WHERE o.status NOT IN ('PLACED','RETURNED', 'CANCELLED')
GROUP BY s.seller_id
ORDER BY 2 DESC;
```
**=> Result:**
```plantuml
"Sort  (cost=3237596.10..3237596.42 rows=130 width=12)"
"  Sort Key: (count(oi.product_id)) DESC"
"  ->  Finalize GroupAggregate  (cost=3237552.33..3237591.53 rows=130 width=12)"
"        Group Key: s.seller_id"
"        ->  Gather Merge  (cost=3237552.33..3237588.67 rows=312 width=12)"
"              Workers Planned: 2"
"              ->  Sort  (cost=3236552.31..3236552.63 rows=130 width=12)"
"                    Sort Key: s.seller_id"
"                    ->  Partial HashAggregate  (cost=3236546.45..3236547.75 rows=130 width=12)"
"                          Group Key: s.seller_id"
"                          ->  Hash Join  (cost=54543.76..3078532.41 rows=31602807 width=8)"
"                                Hash Cond: (o.seller_id = s.seller_id)"
"                                ->  Hash Join  (cost=54530.84..2992857.64 rows=31602807 width=8)"
"                                      Hash Cond: (oi.product_id = p.product_id)"
"                                      ->  Parallel Hash Join  (cost=54486.34..2909504.19 rows=31602807 width=8)"
"                                            Hash Cond: (oi.order_id = o.order_id)"
"                                            ->  Parallel Seq Scan on order_items_old oi  (cost=0.00..2193566.67 rows=63138267 width=8)"
"                                            ->  Parallel Hash  (cost=44220.50..44220.50 rows=625667 width=8)"
"                                                  ->  Parallel Seq Scan on orders_old o  (cost=0.00..44220.50 rows=625667 width=8)"
"                                                        Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                      ->  Hash  (cost=32.00..32.00 rows=1000 width=4)"
"                                            ->  Seq Scan on products p  (cost=0.00..32.00 rows=1000 width=4)"
"                                ->  Hash  (cost=11.30..11.30 rows=130 width=4)"
"                                      ->  Seq Scan on sellers s  (cost=0.00..11.30 rows=130 width=4)"
"JIT:"
"  Functions: 32"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 25 | Query complete 00:00:46.741**

# Optimization:
(Rename orders and order_items to orders_old and order_items_old)
## 1. orders table:
- Partition steps:
```plantuml
--DROP TABLE IF EXISTS public.orders;

--create new table
CREATE TABLE public.orders
(
    order_id SERIAL,
   	order_date TIMESTAMP NOT NULL,
	seller_id INT NOT NULL REFERENCES sellers(seller_id),
	status VARCHAR(20),
	total_amount DECIMAL(12,2),
	created_at TIMESTAMP NOT NULL,
	PRIMARY KEY (order_date, order_id)
)
PARTITION BY RANGE(order_date);

-- add some partitions
CREATE TABLE orders_202808 PARTITION OF orders
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

CREATE TABLE orders_202509 PARTITION OF orders
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
	
CREATE TABLE orders_202510 PARTITION OF orders
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```
**=> Insert data**

- Create indexes
```plantuml
CREATE INDEX idx_order_date ON orders(order_date);
CREATE INDEX idx_seller_id ON orders(seller_id);
```

## 2. order_items table:
- Partition steps:
```plantuml
--DROP TABLE IF EXISTS public.order_items;

CREATE TABLE IF NOT EXISTS public.order_items
(
    order_item_id SERIAL,
    order_id integer NOT NULL,
    product_id integer NOT NULL,
	order_date timestamp NOT NULL,
    quantity integer,
    unit_price numeric(12,2),
    subtotal numeric(12,2),
	created_at timestamp NOT NULL,
	PRIMARY KEY (order_date, order_item_id)
) PARTITION BY RANGE(order_date);

-- add date partitions
CREATE TABLE order_items_202808 PARTITION OF order_items
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

CREATE TABLE order_items_202509 PARTITION OF order_items
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
	
CREATE TABLE order_items_202510 PARTITION OF order_items
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```

**=> Insert data for order_items**

- Create indexes
```plantuml
CREATE INDEX idx_order_items_order_id ON order_items (order_id);
CREATE INDEX idx_order_items_product_id ON order_items (product_id);
CREATE INDEX idx_order_items_date ON order_items (order_date);
```

# After Optimize
### 1. Total revenue per month
```plantuml
"Finalize GroupAggregate  (cost=3650775002.26..3650775064.76 rows=200 width=40)"
"  Group Key: (date_trunc('month'::text, oi.order_date))"
"  ->  Gather Merge  (cost=3650775002.26..3650775058.16 rows=480 width=40)"
"        Workers Planned: 2"
"        ->  Sort  (cost=3650774002.23..3650774002.73 rows=200 width=40)"
"              Sort Key: (date_trunc('month'::text, oi.order_date))"
"              ->  Partial HashAggregate  (cost=3650773991.59..3650773994.59 rows=200 width=40)"
"                    Group Key: date_trunc('month'::text, oi.order_date)"
"                    ->  Nested Loop  (cost=0.44..1285123696.01 rows=473130059115 width=16)"
"                          ->  Parallel Append  (cost=0.00..47344.76 rows=624653 width=4)"
"                                ->  Parallel Seq Scan on orders_202510 o_3  (cost=0.00..14906.65 rows=211549 width=4)"
"                                      Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                ->  Parallel Seq Scan on orders_202808 o_1  (cost=0.00..14890.20 rows=208872 width=4)"
"                                      Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                ->  Parallel Seq Scan on orders_202509 o_2  (cost=0.00..14424.65 rows=204232 width=4)"
"                                      Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                          ->  Append  (cost=0.44..138.88 rows=2481 width=20)"
"                                ->  Index Scan using order_items_202808_order_id_idx on order_items_202808 oi_1  (cost=0.44..42.39 rows=840 width=20)"
"                                      Index Cond: (order_id = o.order_id)"
"                                ->  Index Scan using order_items_202509_order_id_idx on order_items_202509 oi_2  (cost=0.44..41.84 rows=809 width=20)"
"                                      Index Cond: (order_id = o.order_id)"
"                                ->  Index Scan using order_items_202510_order_id_idx on order_items_202510 oi_3  (cost=0.44..42.25 rows=832 width=20)"
"                                      Index Cond: (order_id = o.order_id)"
"JIT:"
"  Functions: 30"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 3 | Query complete 00:03:55.021**

### 2. Orders filtered by seller and date
```plantuml
"WindowAgg  (cost=525334.99..592834.97 rows=3000000 width=32)"
"  Window: w1 AS (ORDER BY (date_trunc('day'::text, orders.order_date)), orders.seller_id ROWS UNBOUNDED PRECEDING)"
"  ->  Sort  (cost=525334.97..532834.97 rows=3000000 width=24)"
"        Sort Key: (date_trunc('day'::text, orders.order_date)), orders.seller_id"
"        ->  Append  (cost=0.00..79534.00 rows=3000000 width=24)"
"              ->  Seq Scan on orders_202808 orders_1  (cost=0.00..21729.63 rows=1010130 width=24)"
"              ->  Seq Scan on orders_202509 orders_2  (cost=0.00..21050.69 rows=978615 width=24)"
"              ->  Seq Scan on orders_202510 orders_3  (cost=0.00..21753.69 rows=1011255 width=24)"
"JIT:"
"  Functions: 9"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 3000000 | Query complete 00:00:10.703**

### 3. Filter data in order_item by product_id
```plantuml
"Sort  (cost=2467949923.62..2467949924.12 rows=200 width=36)"
"  Sort Key: (sum(oi.subtotal))"
"  ->  Finalize GroupAggregate  (cost=2467949853.97..2467949915.97 rows=200 width=36)"
"        Group Key: oi.order_id"
"        ->  Gather Merge  (cost=2467949853.97..2467949909.87 rows=480 width=36)"
"              Workers Planned: 2"
"              ->  Sort  (cost=2467948853.94..2467948854.44 rows=200 width=36)"
"                    Sort Key: oi.order_id"
"                    ->  Partial HashAggregate  (cost=2467948843.80..2467948846.30 rows=200 width=36)"
"                          Group Key: oi.order_id"
"                          ->  Nested Loop  (cost=0.44..102298548.23 rows=473130059115 width=12)"
"                                ->  Parallel Append  (cost=0.00..47344.76 rows=624653 width=4)"
"                                      ->  Parallel Seq Scan on orders_202510 o_3  (cost=0.00..14906.65 rows=211549 width=4)"
"                                            Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                      ->  Parallel Seq Scan on orders_202808 o_1  (cost=0.00..14890.20 rows=208872 width=4)"
"                                            Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                      ->  Parallel Seq Scan on orders_202509 o_2  (cost=0.00..14424.65 rows=204232 width=4)"
"                                            Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                ->  Append  (cost=0.44..138.88 rows=2481 width=12)"
"                                      ->  Index Scan using order_items_202808_order_id_idx on order_items_202808 oi_1  (cost=0.44..42.39 rows=840 width=12)"
"                                            Index Cond: (order_id = o.order_id)"
"                                      ->  Index Scan using order_items_202509_order_id_idx on order_items_202509 oi_2  (cost=0.44..41.84 rows=809 width=12)"
"                                            Index Cond: (order_id = o.order_id)"
"                                      ->  Index Scan using order_items_202510_order_id_idx on order_items_202510 oi_3  (cost=0.44..42.25 rows=832 width=12)"
"                                            Index Cond: (order_id = o.order_id)"
"JIT:"
"  Functions: 30"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 151485743 | Query complete 00:03:33.784**

### 4. Find order with highest total_amount
```plantuml
"Sort  (cost=2467949923.62..2467949924.12 rows=200 width=36)"
"  Sort Key: (sum(oi.subtotal))"
"  ->  Finalize GroupAggregate  (cost=2467949853.97..2467949915.97 rows=200 width=36)"
"        Group Key: oi.order_id"
"        ->  Gather Merge  (cost=2467949853.97..2467949909.87 rows=480 width=36)"
"              Workers Planned: 2"
"              ->  Sort  (cost=2467948853.94..2467948854.44 rows=200 width=36)"
"                    Sort Key: oi.order_id"
"                    ->  Partial HashAggregate  (cost=2467948843.80..2467948846.30 rows=200 width=36)"
"                          Group Key: oi.order_id"
"                          ->  Nested Loop  (cost=0.44..102298548.23 rows=473130059115 width=12)"
"                                ->  Parallel Append  (cost=0.00..47344.76 rows=624653 width=4)"
"                                      ->  Parallel Seq Scan on orders_202510 o_3  (cost=0.00..14906.65 rows=211549 width=4)"
"                                            Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                      ->  Parallel Seq Scan on orders_202808 o_1  (cost=0.00..14890.20 rows=208872 width=4)"
"                                            Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                      ->  Parallel Seq Scan on orders_202509 o_2  (cost=0.00..14424.65 rows=204232 width=4)"
"                                            Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                ->  Append  (cost=0.44..138.88 rows=2481 width=12)"
"                                      ->  Index Scan using order_items_202808_order_id_idx on order_items_202808 oi_1  (cost=0.44..42.39 rows=840 width=12)"
"                                            Index Cond: (order_id = o.order_id)"
"                                      ->  Index Scan using order_items_202509_order_id_idx on order_items_202509 oi_2  (cost=0.44..41.84 rows=809 width=12)"
"                                            Index Cond: (order_id = o.order_id)"
"                                      ->  Index Scan using order_items_202510_order_id_idx on order_items_202510 oi_3  (cost=0.44..42.25 rows=832 width=12)"
"                                            Index Cond: (order_id = o.order_id)"
"JIT:"
"  Functions: 30"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 1499694 | Query complete 00:00:32.470**

### 5. List products with highest quantity sold
```plantuml
"Sort  (cost=51324000608.72..51324001076.22 rows=187000 width=63)"
"  Sort Key: (sum(oi.subtotal)) DESC"
"  ->  Finalize GroupAggregate  (cost=51323918107.21..51323977202.87 rows=187000 width=63)"
"        Group Key: oi.product_id, p.product_name"
"        ->  Gather Merge  (cost=51323918107.21..51323970377.37 rows=448800 width=63)"
"              Workers Planned: 2"
"              ->  Sort  (cost=51323917107.19..51323917574.69 rows=187000 width=63)"
"                    Sort Key: oi.product_id, p.product_name"
"                    ->  Partial HashAggregate  (cost=43931234190.16..51323893701.33 rows=187000 width=63)"
"                          Group Key: oi.product_id, p.product_name"
"                          Planned Partitions: 8"
"                          ->  Hash Join  (cost=44.94..1349528869.81 rows=473130059115 width=39)"
"                                Hash Cond: (oi.product_id = p.product_id)"
"                                ->  Nested Loop  (cost=0.44..102298848.23 rows=473130059115 width=12)"
"                                      ->  Parallel Append  (cost=0.00..47344.76 rows=624653 width=4)"
"                                            ->  Parallel Seq Scan on orders_202510 o_3  (cost=0.00..14906.65 rows=211549 width=4)"
"                                                  Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                            ->  Parallel Seq Scan on orders_202808 o_1  (cost=0.00..14890.20 rows=208872 width=4)"
"                                                  Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                            ->  Parallel Seq Scan on orders_202509 o_2  (cost=0.00..14424.65 rows=204232 width=4)"
"                                                  Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                      ->  Append  (cost=0.44..138.88 rows=2481 width=16)"
"                                            ->  Index Scan using order_items_202808_order_id_idx on order_items_202808 oi_1  (cost=0.44..42.39 rows=840 width=16)"
"                                                  Index Cond: (order_id = o.order_id)"
"                                            ->  Index Scan using order_items_202509_order_id_idx on order_items_202509 oi_2  (cost=0.44..41.84 rows=809 width=16)"
"                                                  Index Cond: (order_id = o.order_id)"
"                                            ->  Index Scan using order_items_202510_order_id_idx on order_items_202510 oi_3  (cost=0.44..42.25 rows=832 width=16)"
"                                                  Index Cond: (order_id = o.order_id)"
"                                ->  Hash  (cost=32.00..32.00 rows=1000 width=31)"
"                                      ->  Seq Scan on products p  (cost=0.00..32.00 rows=1000 width=31)"
"JIT:"
"  Functions: 38"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 1000 | Query complete 00:01:02.277**

### 6. Orders by Seller in October
```plantuml
"Sort  (cost=1492066709.42..1492066774.42 rows=26000 width=334)"
"  Sort Key: (count(o.seller_id))"
"  ->  Finalize GroupAggregate  (cost=1492052741.80..1492060802.31 rows=26000 width=334)"
"        Group Key: s.seller_name, (date_trunc('month'::text, oi.order_date))"
"        ->  Gather Merge  (cost=1492052741.80..1492060009.31 rows=62400 width=334)"
"              Workers Planned: 2"
"              ->  Sort  (cost=1492051741.77..1492051806.77 rows=26000 width=334)"
"                    Sort Key: s.seller_name, (date_trunc('month'::text, oi.order_date))"
"                    ->  Partial HashAggregate  (cost=1221601195.13..1492045834.66 rows=26000 width=334)"
"                          Group Key: s.seller_name, date_trunc('month'::text, oi.order_date)"
"                          Planned Partitions: 4"
"                          ->  Parallel Hash Join  (cost=2515572.74..55204915.93 rows=3077055312 width=330)"
"                                Hash Cond: (o.order_id = oi.order_id)"
"                                ->  Hash Join  (cost=12.93..49147.71 rows=812500 width=326)"
"                                      Hash Cond: (o.seller_id = s.seller_id)"
"                                      ->  Parallel Append  (cost=0.00..45784.00 rows=1250000 width=8)"
"                                            ->  Parallel Seq Scan on orders_202510 o_3  (cost=0.00..13326.56 rows=421356 width=8)"
"                                            ->  Parallel Seq Scan on orders_202808 o_1  (cost=0.00..13311.88 rows=420888 width=8)"
"                                            ->  Parallel Seq Scan on orders_202509 o_2  (cost=0.00..12895.56 rows=407756 width=8)"
"                                      ->  Hash  (cost=11.30..11.30 rows=130 width=322)"
"                                            ->  Seq Scan on sellers s  (cost=0.00..11.30 rows=130 width=322)"
"                                ->  Parallel Hash  (cost=2510073.88..2510073.88 rows=315595 width=12)"
"                                      ->  Parallel Append  (cost=0.00..2510073.88 rows=315595 width=12)"
"                                            ->  Parallel Seq Scan on order_items_202510 oi_3  (cost=0.00..845169.65 rows=106331 width=12)"
"                                                  Filter: (EXTRACT(month FROM order_date) = '10'::numeric)"
"                                            ->  Parallel Seq Scan on order_items_202808 oi_1  (cost=0.00..844792.50 rows=106284 width=12)"
"                                                  Filter: (EXTRACT(month FROM order_date) = '10'::numeric)"
"                                            ->  Parallel Seq Scan on order_items_202509 oi_2  (cost=0.00..818533.75 rows=102980 width=12)"
"                                                  Filter: (EXTRACT(month FROM order_date) = '10'::numeric)"
"JIT:"
"  Functions: 37"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```

**Total rows: 5 | Query complete 00:03:13.340**

### 7. Revenue per Product per Month
```plantuml
"Sort  (cost=57127238706.05..57127239173.55 rows=187000 width=67)"
"  Sort Key: (sum(oi.subtotal))"
"  ->  Finalize GroupAggregate  (cost=57127155096.54..57127214659.70 rows=187000 width=67)"
"        Group Key: p.product_name, (date_trunc('month'::text, oi.order_date))"
"        ->  Gather Merge  (cost=57127155096.54..57127207366.70 rows=448800 width=67)"
"              Workers Planned: 2"
"              ->  Sort  (cost=57127154096.52..57127154564.02 rows=187000 width=67)"
"                    Sort Key: p.product_name, (date_trunc('month'::text, oi.order_date))"
"                    ->  Partial HashAggregate  (cost=48810387924.78..57127130050.16 rows=187000 width=67)"
"                          Group Key: p.product_name, date_trunc('month'::text, oi.order_date)"
"                          Planned Partitions: 8"
"                          ->  Hash Join  (cost=44.94..2532354017.60 rows=473130059115 width=43)"
"                                Hash Cond: (oi.product_id = p.product_id)"
"                                ->  Nested Loop  (cost=0.44..102298848.23 rows=473130059115 width=20)"
"                                      ->  Parallel Append  (cost=0.00..47344.76 rows=624653 width=4)"
"                                            ->  Parallel Seq Scan on orders_202510 o_3  (cost=0.00..14906.65 rows=211549 width=4)"
"                                                  Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                            ->  Parallel Seq Scan on orders_202808 o_1  (cost=0.00..14890.20 rows=208872 width=4)"
"                                                  Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                            ->  Parallel Seq Scan on orders_202509 o_2  (cost=0.00..14424.65 rows=204232 width=4)"
"                                                  Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                      ->  Append  (cost=0.44..138.88 rows=2481 width=24)"
"                                            ->  Index Scan using order_items_202808_order_id_idx on order_items_202808 oi_1  (cost=0.44..42.39 rows=840 width=24)"
"                                                  Index Cond: (order_id = o.order_id)"
"                                            ->  Index Scan using order_items_202509_order_id_idx on order_items_202509 oi_2  (cost=0.44..41.84 rows=809 width=24)"
"                                                  Index Cond: (order_id = o.order_id)"
"                                            ->  Index Scan using order_items_202510_order_id_idx on order_items_202510 oi_3  (cost=0.44..42.25 rows=832 width=24)"
"                                                  Index Cond: (order_id = o.order_id)"
"                                ->  Hash  (cost=32.00..32.00 rows=1000 width=31)"
"                                      ->  Seq Scan on products p  (cost=0.00..32.00 rows=1000 width=31)"
"JIT:"
"  Functions: 38"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```
**Total rows: 2805 | Query complete 00:00:22.763**

### 8. Products Sold per Seller
```plantuml
"Sort  (cost=2414960140.55..2414960140.87 rows=130 width=12)"
"  Sort Key: (count(oi.product_id)) DESC"
"  ->  Finalize GroupAggregate  (cost=2414960096.78..2414960135.98 rows=130 width=12)"
"        Group Key: s.seller_id"
"        ->  Gather Merge  (cost=2414960096.78..2414960133.12 rows=312 width=12)"
"              Workers Planned: 2"
"              ->  Sort  (cost=2414959096.76..2414959097.08 rows=130 width=12)"
"                    Sort Key: s.seller_id"
"                    ->  Partial HashAggregate  (cost=2414959090.89..2414959092.19 rows=130 width=12)"
"                          Group Key: s.seller_id"
"                          ->  Hash Join  (cost=116080.34..877286398.77 rows=307534538425 width=8)"
"                                Hash Cond: (oi.product_id = p.product_id)"
"                                ->  Nested Loop  (cost=116035.84..66586869.17 rows=307534538425 width=8)"
"                                      ->  Merge Join  (cost=116035.40..123219.55 rows=406025 width=8)"
"                                            Merge Cond: (o.seller_id = s.seller_id)"
"                                            ->  Sort  (cost=116019.53..117581.17 rows=624653 width=8)"
"                                                  Sort Key: o.seller_id"
"                                                  ->  Parallel Append  (cost=0.00..47344.76 rows=624653 width=8)"
"                                                        ->  Parallel Seq Scan on orders_202510 o_3  (cost=0.00..14906.65 rows=211549 width=8)"
"                                                              Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                                        ->  Parallel Seq Scan on orders_202808 o_1  (cost=0.00..14890.20 rows=208872 width=8)"
"                                                              Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                                        ->  Parallel Seq Scan on orders_202509 o_2  (cost=0.00..14424.65 rows=204232 width=8)"
"                                                              Filter: ((status)::text <> ALL ('{PLACED,RETURNED,CANCELLED}'::text[]))"
"                                            ->  Sort  (cost=15.86..16.19 rows=130 width=4)"
"                                                  Sort Key: s.seller_id"
"                                                  ->  Seq Scan on sellers s  (cost=0.00..11.30 rows=130 width=4)"
"                                      ->  Append  (cost=0.44..138.88 rows=2481 width=8)"
"                                            ->  Index Scan using order_items_202808_order_id_idx on order_items_202808 oi_1  (cost=0.44..42.39 rows=840 width=8)"
"                                                  Index Cond: (order_id = o.order_id)"
"                                            ->  Index Scan using order_items_202509_order_id_idx on order_items_202509 oi_2  (cost=0.44..41.84 rows=809 width=8)"
"                                                  Index Cond: (order_id = o.order_id)"
"                                            ->  Index Scan using order_items_202510_order_id_idx on order_items_202510 oi_3  (cost=0.44..42.25 rows=832 width=8)"
"                                                  Index Cond: (order_id = o.order_id)"
"                                ->  Hash  (cost=32.00..32.00 rows=1000 width=4)"
"                                      ->  Seq Scan on products p  (cost=0.00..32.00 rows=1000 width=4)"
"JIT:"
"  Functions: 46"
"  Options: Inlining true, Optimization true, Expressions true, Deforming true"
```

**Total rows: 5 | Query complete 00:00:30.031**