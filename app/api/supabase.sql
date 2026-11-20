-- Tablas del asistente bursátil. Se ejecuta en el editor SQL de Supabase; se puede volver a ejecutar completo sin riesgo.
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

-- Tabla centinela del keep-alive (/estado): una fila que solo ve la clave de servicio.
-- Con una clave sin permisos, RLS la filtra a vacío y la API informa supabase_ok: false.
create table if not exists salud (id int primary key);
insert into salud (id) values (1) on conflict do nothing;
alter table salud enable row level security;

-- Permisos mínimos para la clave de servicio: los proyectos nuevos de Supabase no los conceden por defecto
-- (sin ellos, cada consulta responde 42501 "permission denied"). A anon y authenticated se les retira todo,
-- por si el proyecto es antiguo y traía permisos por defecto (RLS sin políticas ya los bloquea igual).
grant usage on schema public to service_role;
grant select, insert         on decisiones      to service_role;
grant usage, select          on sequence decisiones_id_seq to service_role;
grant select, insert, update on niveles_usuario to service_role;
grant select                 on salud           to service_role;
revoke all on decisiones, niveles_usuario, salud from anon, authenticated;
revoke all on sequence decisiones_id_seq from anon, authenticated;
