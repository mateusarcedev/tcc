import { Text, View } from "react-native";
import { styles } from './style';
import React from 'react';

interface LabelProps {
  categoria: string;
  cor: string;
}

export default function Label({ categoria, cor }: LabelProps) {
  return (
    <View style={styles.container}>
      <View style={{
        backgroundColor: cor,
        width: 15,
        height: 15,
        borderRadius: 500,
      }}>

      </View>
      <Text style={styles.category}>
        {categoria}
      </Text>
    </View>
  );
}
