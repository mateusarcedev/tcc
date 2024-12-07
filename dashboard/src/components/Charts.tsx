"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

const COLORS = ['#0088FE', '#FF8042'];

export function Charts() {
  const [data, setData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [timeData, setTimeData] = useState([]);

  useEffect(() => {
    // Função para buscar os dados da API
    const fetchData = async () => {
      try {
        const [statusRes, categoryRes, timeRes] = await Promise.all([
          axios.get("http://localhost:8000/api/status"),
          axios.get("http://localhost:8000/api/categories"),
          axios.get("http://localhost:8000/api/time"),
        ]);

        setData(statusRes.data); // Formato esperado: [{ name: 'Válidos', value: 1043 }, { name: 'Inválidos', value: 191 }]
        setCategoryData(categoryRes.data); // Formato esperado: [{ name: 'smartphones', quantidade: 450 }, ...]
        setTimeData(timeRes.data); // Formato esperado: [{ name: '00:00', produtos: 42 }, ...]
      } catch (error) {
        console.error("Erro ao buscar dados da API:", error);
      }
    };

    // Busca inicial
    fetchData();

    // Atualizar a cada 5 segundos
    const intervalId = setInterval(fetchData, 5000);

    // Limpa o intervalo ao desmontar o componente
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Status dos Produtos</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Produtos por Categoria</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={categoryData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="quantidade" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Produtos Processados por Hora</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="produtos" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
