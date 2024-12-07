import { Text, View } from "react-native";
import { styles } from './style';
import React from 'react';

interface CardChartsProps {
  quantidade: number;
  icon: React.ReactNode;
  status: string;
}

export default function CardCharts({ quantidade, icon, status }: CardChartsProps) {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text>
          {icon}
        </Text>
      </View>
      <Text style={styles.quantity}>
        {quantidade}
      </Text>
      <Text style={styles.status}>
        {status}
      </Text>
    </View>
  );
}
