"use client";

import axios from 'axios';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { CheckCircle, Smartphone, XCircle } from 'lucide-react';

export function SummaryCards() {
  const [totalItens, setTotalItens] = useState(0);
  const [totalValidos, setTotalValidos] = useState(0);
  const [totalInvalidos, setTotalInvalidos] = useState(0);
  const [taxaSucesso, setTaxaSucesso] = useState(null); // Alterado para `null` inicialmente

  // Função para buscar dados da API
  const fetchData = async () => {
    try {
      // Requisições para buscar os dados
      const [
        totalItensRes,
        totalValidosRes,
        totalInvalidosRes,
        taxaSucessoRes,  // Nova requisição para a taxa de sucesso
      ] = await Promise.all([
        axios.get('http://localhost:8000/api/total_itens'),
        axios.get('http://localhost:8000/api/total_validos'),
        axios.get('http://localhost:8000/api/total_invalidos'),
        axios.get('http://localhost:8000/api/taxa_sucesso'),  // Endpoint para a taxa de sucesso
      ]);

      setTotalItens(totalItensRes.data.total_itens);
      setTotalValidos(totalValidosRes.data.total_validos);
      setTotalInvalidos(totalInvalidosRes.data.total_invalidos);
      setTaxaSucesso(taxaSucessoRes.data.taxa_sucesso); // Armazena a taxa de sucesso aqui
    } catch (error) {
      console.error("Erro ao buscar dados da API", error);
    }
  };

  // Atualiza a cada 5 segundos
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Atualiza a cada 5 segundos
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {/* Total Processado */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Processado</CardTitle>
          <Smartphone className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalItens || 0}</div>
          <p className="text-xs text-muted-foreground">Produtos</p>
        </CardContent>
      </Card>

      {/* Produtos Válidos */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Produtos Válidos</CardTitle>
          <CheckCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalValidos || 0}</div>
          <p className="text-xs text-muted-foreground">
            {totalItens > 0 && ((totalValidos / totalItens) * 100).toFixed(1)}% do total
          </p>
        </CardContent>
      </Card>

      {/* Produtos Inválidos */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Produtos Inválidos</CardTitle>
          <XCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalInvalidos || 0}</div>
          <p className="text-xs text-muted-foreground">
            {totalItens > 0 && ((totalInvalidos / totalItens) * 100).toFixed(1)}% do total
          </p>
        </CardContent>
      </Card>

      {/* Taxa de Sucesso */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Taxa de Sucesso</CardTitle>
          <CheckCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {taxaSucesso !== null ? `${taxaSucesso}%` : "Carregando..."}
          </div>
          <p className="text-xs text-muted-foreground">Taxa de sucesso atual</p>
        </CardContent>
      </Card>
    </div>
  );
}
