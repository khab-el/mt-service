CREATE TABLE public.users (
	id serial4 NOT NULL,
	sub uuid NOT NULL,
	account_login int4 NULL,
	"name" varchar NULL,
	code varchar NULL,
	email varchar NULL,
	is_pay_flg bool NULL,
	CONSTRAINT users_pkey PRIMARY KEY (id),
	CONSTRAINT users_sub_code_key UNIQUE (sub, code, account_login, email)
);

CREATE TABLE public."subscription" (
	id serial4 NOT NULL,
	user_id int4 NULL,
	"start" timestamp NULL,
	"end" timestamp NULL,
	CONSTRAINT subscription_pkey PRIMARY KEY (id),
	CONSTRAINT subscription_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE INDEX ix_subscription_id ON public.subscription USING btree (id);

CREATE TABLE public.referal (
	id serial4 NOT NULL,
	user_id int4 NULL,
	referal_id int4 NULL,
	referal float8 NULL,
	is_receive_flg bool NULL,
	CONSTRAINT referal_pkey PRIMARY KEY (id),
	CONSTRAINT referal_referal_id_fkey FOREIGN KEY (referal_id) REFERENCES public.users(id),
	CONSTRAINT referal_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE INDEX ix_referal_id ON public.referal USING btree (id);

CREATE TABLE public.links (
	id serial4 NOT NULL,
	"source" int4 NULL,
	target int4 NULL,
	CONSTRAINT links_pkey PRIMARY KEY (id),
	CONSTRAINT links_source_fkey FOREIGN KEY ("source") REFERENCES public.users(id),
	CONSTRAINT links_target_fkey FOREIGN KEY (target) REFERENCES public.users(id)
);
CREATE INDEX ix_links_id ON public.links USING btree (id);

CREATE TABLE public.orders (
	order_symbol varchar(255) NOT NULL,
	order_ticket int4 NOT NULL,
	order_type varchar(255) NULL,
	order_volume float8 NULL,
	order_price float8 NULL,
	order_time timestamp NULL,
	order_profit float8 NULL,
	order_swap float8 NULL,
	order_sl float8 NULL,
	order_tp float8 NULL,
	account_login int4 NOT NULL,
	order_is_closed bool NOT NULL,
	CONSTRAINT orders_pk PRIMARY KEY (account_login, order_symbol, order_ticket)
);
CREATE INDEX orders_account_login_idx ON public.orders USING btree (account_login, order_time) WHERE (order_is_closed = true);
CREATE INDEX orders_account_login_sym_idx ON public.orders USING brin (account_login) WHERE (order_is_closed = true);

CREATE TABLE public.accounts (
  account_login int4 NOT NULL,
  initial_balance float8 NULL,
  minimal_balance float8 NULL,
  account_balance float8 NULL,
  account_equity float8 NULL,
  account_profit float8 NULL,
  account_margin float8 NULL,
  account_margin_free float8 NULL,
  account_margin_level float8 NULL,
  max_peak float8 NULL,
  next_min_peak float8 NULL,
  abs_drawdown float8 NULL,
  max_drawdown float8 NULL,
  max_drawdown_perc float8 NULL,
  server_time timestamp NULL,
  CONSTRAINT newtable_pkey1 PRIMARY KEY (account_login)
);