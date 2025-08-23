# Navega até a pasta do projeto
Set-Location "D:\Projetos\LechareEducacional"

Write-Host "=== Adicionando todos os arquivos alterados ===" -ForegroundColor Cyan
git add .

Write-Host "=== Commitando alterações ===" -ForegroundColor Cyan
git commit -m "Atualização automática do projeto"

Write-Host "=== Enviando para o GitHub ===" -ForegroundColor Cyan
git push origin main

Write-Host "=== Processo concluído! ===" -ForegroundColor Green
