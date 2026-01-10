#!/bin/bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout waves-tls.key \
  -out waves-tls.crt \
  -subj "/CN=waves.local/O=waves"
