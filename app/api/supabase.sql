-- Tablas del asistente bursátil. Se ejecuta UNA vez en el editor SQL de Supabase (idempotente).
-- Solo guarda alias, decisiones y niveles: sin datos personales.

create table if not exists decisiones (
  id      bigserial primary key,
  alias   text not null,
  fecha   timestamptz not null default now(),
  ticker  text not null,
  nivel   text not null,
  lectura jsonb,
  nota    text
);
create index if not exists decisiones_alias_fecha_idx on decisiones (alias, fecha desc);

create table if not exists niveles_usuario (
  alias       text not null,
  ticker      text not null,
  entradas    jsonb not null,
  salidas     jsonb not null,
  actualizado timestamptz not null default now(),
  primary key (alias, ticker)
);

-- Seguridad: RLS activado y SIN políticas. La clave pública (anon) no lee ni escribe nada;
-- la clave del rol de servicio (secreto SUPABASE_KEY de la API) omite RLS.
alter table decisiones       enable row level security;
alter table niveles_usuario  enable row level security;
