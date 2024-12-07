import * as React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Home from './src/pages/Home';
import CorrectsPackages from './src/pages/CorrectsPackages';
import IncorrectsPackages from './src/pages/IncorrectsPackages'

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={Home} options={{ headerShown: false }} />
        <Stack.Screen
          name="Pacotes Corretos"
          component={CorrectsPackages}
          options={{
            headerStyle: { backgroundColor: '#121214' }, // Ajuste aqui
            headerTintColor: '#fff', // Adicione se precisar mudar a cor do texto do cabeçalho
          }}
        />
        <Stack.Screen
          name="Pacotes Incorretos"
          component={IncorrectsPackages}
          options={{
            headerStyle: { backgroundColor: '#121214' }, // Ajuste aqui
            headerTintColor: '#fff', // Adicione se precisar mudar a cor do texto do cabeçalho
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
