"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { api } from "@/lib/api";

type StatusDatum = { name: string; value: number };
type CategoryDatum = { name: string; quantidade: number };
type TimeDatum = { name: string; produtos: number };

const COLORS = ["#0088FE", "#FF8042"];

export function Charts() {
  const [statusData, setStatusData] = useState<StatusDatum[]>([]);
  const [categoryData, setCategoryData] = useState<CategoryDatum[]>([]);
  const [timeData, setTimeData] = useState<TimeDatum[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusRes, categoryRes, timeRes] = await Promise.all([
          api.get<StatusDatum[]>("/api/status"),
          api.get<CategoryDatum[]>("/api/categories"),
          api.get<TimeDatum[]>("/api/time"),
        ]);

        setStatusData(statusRes.data);
        setCategoryData(categoryRes.data);
        setTimeData(timeRes.data);
      } catch (error) {
        console.error("Erro ao buscar dados da API:", error);
      }
    };

    fetchData();
    const intervalId = window.setInterval(fetchData, 5000);
    return () => window.clearInterval(intervalId);
  }, []);

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div className="rounded-lg bg-white p-4 shadow">
        <h3 className="mb-4 text-lg font-semibold">Status dos produtos</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={statusData}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={80}
              dataKey="value"
            >
              {statusData.map((entry, index) => (
                <Cell key={`${entry.name}-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="rounded-lg bg-white p-4 shadow">
        <h3 className="mb-4 text-lg font-semibold">Produtos por categoria</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={categoryData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Bar dataKey="quantidade" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="rounded-lg bg-white p-4 shadow">
        <h3 className="mb-4 text-lg font-semibold">Produtos processados por hora</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="produtos" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
