#!/bin/bash
# Script para conectar ao banco de dados local
export PGPASSWORD=godrive_dev_password
psql -h localhost -U godrive -d godrive_db "$@"
