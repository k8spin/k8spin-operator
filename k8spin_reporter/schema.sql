CREATE TABLE space_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  organization_name varchar(500),
  tenant_name varchar(500),
  space_name varchar(500),
  cpu float,
  memory float,
);