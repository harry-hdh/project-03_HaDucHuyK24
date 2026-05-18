## 1. Monthly Revenue Report
- Goal: Show total revenue and total orders per month.
- Columns: `month`, `total_orders`, `total_quantity`, `total_revenue`
- Filter: Orders within a specific date range (`start_date` to `end_date`)
```plantuml
CREATE OR REPLACE FUNCTION get_monthly_revenue_report(start_date DATE, end_date DATE)
RETURNS TABLE (
    Month TEXT,
    total_orders BIGINT,
    total_quantity numeric,
    total_revenue numeric
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
	WITH count_quanity AS(
		SELECT order_id,
		count(quantity) as quantity_per_order,
		SUM(subtotal) AS total_per_order
		FROM order_items
		GROUP BY order_id
	)
	SELECT  EXTRACT(MONTH FROM o.order_date)::TEXT AS Month,
			count(o.order_id) AS total_orders,
			SUM(cq.quantity_per_order) AS total_quantity,
			SUM(cq.total_per_order) AS total_revenue
	FROM orders o
	JOIN count_quanity cq ON o.order_id = cq.order_id
	WHERE o.order_date BETWEEN start_date AND end_date
	GROUP BY 1
	ORDER BY 1;
END;
$$;
```

```
SELECT * FROM get_monthly_revenue_report('2025/08/01', '2025/10/01');
```

| month | total_order | total_quantity | total_revenue     |
|-------|-------------|----------------|-------------------|
| 8     | 1010130     | 51016242       | 15242241059877.20 |
| 9     | 978615      | 49430519       | 14768447931547.47 |

**Total rows: 2 | Query complete 00:03:49.698**

## 2. Daily Revenue Report
- Goal: Show total revenue and total orders per month.
- Columns: `date`, `total_orders`, `total_quantity`, `total_revenue`
- Filter: Orders within a specific date range (`start_date` to `end_date`) and *product list*

```plantuml
CREATE OR REPLACE FUNCTION get_daily_revenue_report(start_date DATE, end_date DATE)
RETURNS TABLE (
    Date DATE,
    total_orders BIGINT,
    total_quantity numeric,
    total_revenue numeric
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
	WITH count_quanity AS(
		SELECT order_id,
		count(quantity) as quantity_per_order,
		SUM(subtotal) AS total_per_order
		FROM order_items
		GROUP BY order_id
	)
	SELECT  DATE_TRUNC('day', o.order_date)::DATE AS Date,
			count(o.order_id) AS total_orders,
			SUM(cq.quantity_per_order) AS total_quantity,
			SUM(cq.total_per_order) AS total_revenue
	FROM orders o
	JOIN count_quanity cq ON o.order_id = cq.order_id
	WHERE o.order_date BETWEEN start_date AND end_date
	GROUP BY 1
	ORDER BY 1;
END;
$$;
```

```plantuml
SELECT * FROM get_daily_revenue_report('2025/09/01', '2025/10/01');
```

| date        | total_orders | total_quantity | total_revenue    |
|-------------|--------------|----------------|------------------|
| 2025-09-01  | 32719        | 1648676        | 492866323034.84  |
| 2025-09-02  | 32674        | 1659557        | 495588817451.81  |
| 2025-09-03  | 33014        | 1669885        | 499248601851.94  |

**Total rows: 30 | Query complete 00:01:17.103**

## 3. Seller Performance Report
- Goal: Compare sellers by total revenue and quantity sold.
- Columns: `seller_id`, `seller_name`, `total_orders`, `total_quantity`, `total_revenue`
- Filter: Orders within a specific date range. Optional filter by `category_id` or `brand_id`.

```plantuml
CREATE OR REPLACE FUNCTION get_seller_perform_report(
	start_date DATE, 
	end_date DATE, 
	p_category_id INT DEFAULT NULL, 
	p_brand_id INT DEFAULT NULL
)
RETURNS TABLE (
    seller_id INT,
    seller_name VARCHAR,
    total_orders BIGINT,
    total_quantity BIGINT,
    total_revenue NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
	RETURN QUERY
	SELECT  s.seller_id,
			s.seller_name,
			COUNT(DISTINCT o.order_id) AS total_orders,
			SUM(oi.quantity) AS total_quantity,
			SUM(oi.subtotal) AS total_revenue
	FROM orders o
	JOIN order_items oi ON o.order_id = oi.order_id
	JOIN sellers s ON o.seller_id = s.seller_id
	LEFT JOIN products p ON p.product_id = oi.product_id
	WHERE o.order_date BETWEEN start_date AND end_date
		AND (p_category_id IS NULL OR p.category_id = p_category_id)
		AND (p_brand_id IS NULL OR p.brand_id = p_brand_id)
	GROUP BY 1,2
	ORDER BY 1;
END;
$$;
```

```
SELECT * FROM get_seller_perform_report('2025/09/01', '2025/09/10', 1, 2);
```

| seller_id | seller_name               | total_orders | total_quantity | total_revenue  |
|-----------|---------------------------|--------------|----------------|----------------|
| 1         | Mai Công ty TNHH          | 15725        | 18073          | 4443349055.37  |
| 2         | Dương Công ty TNHH MTV    | 15418        | 17812          | 4369567741.71  |
| 3         | Phạm Công ty Hợp danh     | 15700        | 18044          | 4437073105.54  |
| 4         | Lê và Đặng Công ty TNHH   | 15455        | 17717          | 4353005475.91  |
| 5         | Dương Công ty TNHH        | 15405        | 17735          | 4371433894.62  |

**Total rows: 5 | Query complete 00:02:58.579**

## 4. Top Products per Brand
- Goal: Identify top products for each brand by quantity sold.
- Columns: `brand_id`, `brand_name`, `product_id`, `product_name`, `total_quantity`, `total_revenue`
- Filter: Orders within a specific date range. Optional filter by seller list.

```plantuml
CREATE OR REPLACE FUNCTION get_top_products_per_brand(
    start_date DATE, 
    end_date DATE, 
    seller_ids INT[] DEFAULT NULL
)
RETURNS TABLE (
    b_id INT,
    b_name VARCHAR,
    p_id INT,
    p_name VARCHAR,
    total_quantity BIGINT,
    total_revenue NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
	WITH ProductSales AS (
        SELECT 
            b.brand_id,
            b.brand_name,
            p.product_id,
            p.product_name,
            SUM(oi.quantity) AS sum_qty,
            SUM(oi.subtotal) AS sum_rev,
            RANK() OVER (PARTITION BY b.brand_id ORDER BY SUM(oi.quantity) DESC) as product_rank
        FROM brands b
        JOIN products p ON b.brand_id = p.brand_id
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_date BETWEEN start_date AND end_date
          AND (seller_ids IS NULL OR o.seller_id = ANY(seller_ids))
		  --AND o.seller_id IN(1,5,20)
        GROUP BY 1,2,3,4
    )
    SELECT 
        brand_id, 
        brand_name, 
        product_id, 
        product_name, 
        sum_qty, 
        sum_rev
    FROM ProductSales
    WHERE product_rank = 1
    ORDER BY brand_name;
END;
$$;
```

```plantuml
SELECT * FROM get_top_products_per_brand('2025/08/01', '2025/08/19');
```
| b_id | b_name        | p_id  | p_name                         | total_quantity | total_revenue  |
|------|---------------|-------|--------------------------------|----------------|----------------|
| 15   | Amazon Basics | 866   | Samsung Ergonomic Water Bottle | 29885          | 7449211605.60  |
| 13   | Apple         | 34    | LG Handcrafted Tablet          | 29913          | 5137796754.87  |
| 12   | Bose          | 346   | Dyson Smart Camera             | 29879          | 4897107445.63  |

**Total rows: 22 | Query complete 00:00:55.802**

```plantuml
SELECT * FROM get_top_products_per_brand('2025/09/01', '2025/09/19', ARRAY[1,5,20,10]);
```
| b_id | b_name        | p_id | p_name                       | total_quantity | total_revenue |
|------|---------------|------|------------------------------|----------------|---------------|
| 15   | Amazon Basics | 668  | Panasonic Classic Smartwatch | 12041          | 1905154353.07 |
| 13   | Apple         | 214  | HP Compact Monitor           | 12078          | 5886501360.30 |
| 12   | Bose          | 982  | Nike Lightweight Monitor     | 12125          | 5274644660.00 |

**Total rows: 20 | Query complete 00:00:09.587**

## 5. Orders Status Summary
- Goal:Count orders per status (completed, pending, cancelled).
- Columns:`status`, `total_orders`, `total_revenue`
- Filter:** Orders within a specific date range; optionally filter by *seller list* or *category list*.

```plantuml
CREATE OR REPLACE FUNCTION get_status_summary(
    start_date DATE, 
    end_date DATE, 
    seller_ids INT[] DEFAULT NULL,
	categories_lst INT[] DEFAULT NULL
)
RETURNS TABLE (
	status VARCHAR,
    total_order BIGINT,
    total_revenue NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
	SELECT o.status,
		SUM(oi.quantity) AS sum_qty,
		SUM(oi.subtotal) AS sum_rev
	FROM orders o
	JOIN order_items oi ON oi.order_id = o.order_id
	JOIN products p ON p.product_id = oi.product_id
	JOIN categories c ON c.category_id = p.category_id
	WHERE o.order_date BETWEEN start_date AND end_date
		 AND (seller_ids IS NULL OR o.seller_id = ANY(seller_ids))
		 AND (categories_lst IS NULL OR c.category_id = ANY(categories_lst))
	GROUP BY 1;
END;
$$;
```

```plantuml
SELECT * FROM get_status_summary('2025/09/26', '2025/10/14');
```
| status     | total_orders  | total_revenue     |
|------------|---------------|-------------------|
| CANCELLED  | 4946504       | 1477545302676.50  |
| DELIVERED  | 4946782       | 1477771376355.42  |
| PAID       | 4915968       | 1468538466005.58  |
| PLACED     | 4924551       | 1471105651414.61  |
| RETURNED   | 4922233       | 1470744088836.70  |
| SHIPPED    | 4920734       | 1470469110619.73  |

**Total rows: 6 | Query complete 00:00:16.921**

```plantuml
SELECT * FROM get_status_summary('2025/08/11', '2025/09/02', ARRAY[6,3,11,16], ARRAY[3,10,8]);
```
| status     | total_orders  | total_revenue   |
|------------|---------------|-----------------|
| CANCELLED  | 376608        | 117305179857.19 |
| DELIVERED  | 377911        | 117835499176.63 |
| PAID       | 375295        | 116978212983.88 |
| PLACED     | 383631        | 119569817227.71 |
| RETURNED   | 382903        | 119293737373.55 |
| SHIPPED    | 379980        | 118403496511.79 |

**Total rows: 6 | Query complete 00:00:41.044**