CREATE TABLE IF NOT EXISTS user (
    id INTEGER NOT NULL,
    password VARCHAR NOT NULL,
    token VARCHAR,
    balance DECIMAL(15, 12) NOT NULL DEFAULT 0,
    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_user_password ON user (password);
CREATE UNIQUE INDEX IF NOT EXISTS ix_user_token ON user (token);
CREATE INDEX IF NOT EXISTS ix_user_id ON user (id);

CREATE TABLE IF NOT EXISTS payment (
    id INTEGER NOT NULL,
    payment_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES user (id)
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_payment_payment_id ON payment (payment_id);
CREATE INDEX IF NOT EXISTS ix_payment_id ON payment (id);

CREATE TABLE IF NOT EXISTS os (
    id INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS ix_os_id ON os (id);

CREATE TABLE IF NOT EXISTS vds (
    id INTEGER NOT NULL,
    cores INTEGER NOT NULL,
    ram INTEGER NOT NULL,
    disk_size INTEGER NOT NULL,
    ipv4 BOOLEAN NOT NULL,
    ipv6 BOOLEAN NOT NULL,
    price INTEGER NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS ix_vds_id ON vds (id);

CREATE TABLE IF NOT EXISTS node (
    id INTEGER NOT NULL,
    ip VARCHAR NOT NULL,
    cores INTEGER NOT NULL,
    cores_available INTEGER NOT NULL,
    ram INTEGER NOT NULL,
    ram_available INTEGER NOT NULL,
    disk_size INTEGER NOT NULL,
    disk_size_available INTEGER NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS ix_node_id ON node (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_node_ip ON node (ip);

CREATE TABLE IF NOT EXISTS server (
    id INTEGER NOT NULL,
    vnc_port INTEGER NOT NULL,
    start_at TIMESTAMP NOT NULL,
    end_at TIMESTAMP NOT NULL,
    vds_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(vds_id) REFERENCES vds (id),
    FOREIGN KEY(node_id) REFERENCES node (id),
    FOREIGN KEY(user_id) REFERENCES user (id)
);
CREATE INDEX IF NOT EXISTS ix_server_id ON server (id);

CREATE TABLE IF NOT EXISTS promo (
    id INTEGER NOT NULL,
    code VARCHAR NOT NULL,
    days INTEGER NOT NULL,
    vds_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(vds_id) REFERENCES vds (id)
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_promo_code ON promo (code);
CREATE INDEX IF NOT EXISTS ix_promo_id ON promo (id);
