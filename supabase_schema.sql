-- Tabla para almacenar histórico de VPD de múltiples fincas
CREATE TABLE IF NOT EXISTS vpd_historico (
    id BIGSERIAL PRIMARY KEY,
    finca TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    dia_semana TEXT NOT NULL,
    temperatura DECIMAL(5,2) NOT NULL,
    humedad DECIMAL(5,2) NOT NULL,
    vpd DECIMAL(5,3) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para mejorar rendimiento de consultas
CREATE INDEX IF NOT EXISTS idx_vpd_finca ON vpd_historico(finca);
CREATE INDEX IF NOT EXISTS idx_vpd_timestamp ON vpd_historico(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_vpd_finca_timestamp ON vpd_historico(finca, timestamp DESC);

-- Comentarios en tabla y columnas
COMMENT ON TABLE vpd_historico IS 'Histórico de mediciones VPD de múltiples fincas';
COMMENT ON COLUMN vpd_historico.finca IS 'Identificador de la finca (PYGANFLOR, FINCA2, FINCA3)';
COMMENT ON COLUMN vpd_historico.timestamp IS 'Marca de tiempo de la medición';
COMMENT ON COLUMN vpd_historico.temperatura IS 'Temperatura en grados Celsius';
COMMENT ON COLUMN vpd_historico.humedad IS 'Humedad relativa en porcentaje';
COMMENT ON COLUMN vpd_historico.vpd IS 'Déficit de Presión de Vapor en kPa';
