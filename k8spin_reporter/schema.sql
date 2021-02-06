CREATE TABLE organization (
  id VARCHAR(250) PRIMARY KEY,
  name varchar(250)
);
CREATE TABLE organization_resources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  organization_id VARCHAR(250),
  cpu float,
  memory float,
  FOREIGN KEY(organization_id) REFERENCES organization(id)
);
CREATE TABLE tenant (
  id VARCHAR(250) PRIMARY KEY,
  name varchar(250),
  organization_id VARCHAR(250),
  FOREIGN KEY(organization_id) REFERENCES organization(id)
);
CREATE TABLE tenant_resources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  tenant_id VARCHAR(250),
  cpu float,
  memory float,
  FOREIGN KEY(tenant_id) REFERENCES tenant(id)
);
CREATE TABLE space (
  id VARCHAR(250) PRIMARY KEY,
  name varchar(250),
  organization_id VARCHAR(250),
  tenant_id VARCHAR(250),
  FOREIGN KEY(organization_id) REFERENCES organization(id),
  FOREIGN KEY(tenant_id) REFERENCES tenant(id)
);
CREATE TABLE space_resources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  space_id VARCHAR(250),
  cpu float,
  memory float,
  FOREIGN KEY(space_id) REFERENCES space(id)
);
CREATE TABLE space_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  organization_id varchar(250),
  tenant_id varchar(250),
  space_id varchar(250),
  cpu float,
  memory float,
  FOREIGN KEY(organization_id) REFERENCES organization(id),
  FOREIGN KEY(tenant_id) REFERENCES tenant(id),
  FOREIGN KEY(space_id) REFERENCES space(id)
);