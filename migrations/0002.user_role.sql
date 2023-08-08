ALTER TABLE public.users ADD is_admin bool;
ALTER TABLE public.users DROP COLUMN is_confirm_pay;
ALTER TABLE public.users DROP COLUMN is_pay_flg;

ALTER TABLE public.users ADD is_stratagy_buy bool;
ALTER TABLE public.users ADD is_confirm_stratagy bool;
ALTER TABLE public.users ADD is_subscription_buy bool;
ALTER TABLE public.users ADD is_confirm_subscription bool;

DROP TABLE subscription;
CREATE TABLE subscription (
    id serial4 NOT NULL,
	user_id int4 NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    valid_from timestamp(0) without time zone DEFAULT now() NOT NULL,
    valid_to timestamp(0) without time zone DEFAULT (date_trunc('month', now()) + interval '1 month - 1 second')::timestamp NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT subscription_check CHECK ((valid_from < valid_to)),
    CONSTRAINT subscription_user_id_valid_from_key UNIQUE (user_id, valid_from) DEFERRABLE,
    CONSTRAINT subscription_user_id_valid_to_key UNIQUE (user_id, valid_to) DEFERRABLE,
    CONSTRAINT subscription_user_id_valid_from_valid_to_key UNIQUE (user_id, valid_from, valid_to) DEFERRABLE,
    CONSTRAINT subscription_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
