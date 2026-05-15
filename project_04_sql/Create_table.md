## Recreate order_items table
```plantuml
-- DROP TABLE IF EXISTS public.order_items;

CREATE TABLE IF NOT EXISTS public.order_items
(
    order_item_id SERIAL PRIMARY KEY,
    order_id integer NOT NULL,
    product_id integer NOT NULL,
	order_date timestamp,
    quantity integer,
    unit_price numeric(12,2),
    subtotal numeric(12,2),
	created_at timestamp,
    CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id)
        REFERENCES public.orders (order_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id)
        REFERENCES public.products (product_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.order_items
    OWNER to hdhpg;
```
