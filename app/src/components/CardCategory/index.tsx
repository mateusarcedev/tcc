import { Text, View } from "react-native";
import { styles } from './style';
import React from 'react';

interface CardCategoryProps {
  icon: React.ReactNode;
}

export default function CardCategory({ icon }: CardCategoryProps) {
  return (
    <View style={styles.container}>
      <Text>
        {icon}
      </Text>
    </View>
  );
}
