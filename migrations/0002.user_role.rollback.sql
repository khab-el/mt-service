ALTER TABLE public.users DROP COLUMN is_admin;
ALTER TABLE public.users ADD is_confirm_pay bool;
ALTER TABLE public.users ADD is_pay_flg bool;

ALTER TABLE public.users DROP COLUMN is_stratagy_buy bool;
ALTER TABLE public.users DROP COLUMN is_confirm_stratagy bool;
ALTER TABLE public.users DROP COLUMN is_subscription_buy bool;
ALTER TABLE public.users DROP COLUMN is_confirm_subscription bool;

DROP TABLE subscription;
CREATE TABLE public."subscription" (
	id serial4 NOT NULL,
	user_id int4 NULL,
	"start" timestamp NULL,
	"end" timestamp NULL,
	CONSTRAINT subscription_pkey PRIMARY KEY (id),
	CONSTRAINT subscription_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE INDEX ix_subscription_id ON public.subscription USING btree (id);