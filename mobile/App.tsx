/**
 * GoDrive Mobile - Main App Entry
 *
 * Configuração do QueryClientProvider, NavigationContainer e providers globais.
 */

import './global.css';
import React, { useEffect } from 'react';
import { StyleSheet, ActivityIndicator, View, Text, Linking, Platform } from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import * as ExpoLinking from 'expo-linking';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { QueryClientProvider } from '@tanstack/react-query';
import { NavigationContainer } from '@react-navigation/native';
import {
  useFonts,
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  Inter_700Bold,
} from '@expo-google-fonts/inter';
import { queryClient } from './src/lib/queryClient';
import { useAuthStore, type User } from './src/lib/store';
import { api, tokenManager } from './src/lib';
import { AuthNavigator } from './src/features/auth';
import { RootNavigator } from './src/navigation';

/**
 * Tela de loading enquanto verifica autenticação.
 */
function LoadingScreen() {
  return (
    <View style={styles.loadingContainer}>
      <Text style={styles.loadingLogo}>🚗</Text>
      <Text style={styles.loadingTitle}>GoDrive</Text>
      <ActivityIndicator size="large" color="#135bec" style={styles.spinner} />
    </View>
  );
}

// MainNavigator removed in favor of StudentTabNavigator


export default function App() {
  const [fontsLoaded] = useFonts({
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    Inter_700Bold,
  });

  const { isAuthenticated, isLoading, setUser, setLoading } = useAuthStore();

  useEffect(() => {
    const checkAuth = async () => {
      setLoading(true);
      try {
        const hasToken = await tokenManager.hasValidToken();
        if (hasToken) {
          try {
            const { data } = await api.get<User>('/auth/me');
            setUser(data);
          } catch {
            await tokenManager.clearTokens();
            setUser(null);
          }
        } else {
          setUser(null);
        }
      } catch {
        setUser(null);
      }
    };

    checkAuth();
  }, [setLoading, setUser]);

  // Deep link: fechar Safari View Controller no iOS após retorno do checkout
  useEffect(() => {
    const subscription = Linking.addEventListener('url', (event) => {
      // Aceita tanto godrive:// quanto o scheme do Expo Go (exp://)
      if (event.url && (event.url.includes('godrive://') || event.url.includes(ExpoLinking.createURL('')))) {
        if (Platform.OS === 'ios') {
          WebBrowser.dismissBrowser();
        }
      }
    });
    return () => subscription.remove();
  }, []);

  // Configuração de deep links para NavigationContainer
  const linking = {
    prefixes: ['godrive://', ExpoLinking.createURL('/')],
    config: {
      screens: {
        PaymentResult: 'payment/:status',
      },
    },
  };

  if (!fontsLoaded) {
    return <LoadingScreen />;
  }

  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <SafeAreaView style={styles.container}>
          <StatusBar style="dark" />

          {isLoading ? (
            <LoadingScreen />
          ) : (
            <NavigationContainer linking={linking}>
              {isAuthenticated ? <RootNavigator /> : <AuthNavigator />}
            </NavigationContainer>
          )}
        </SafeAreaView>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  // Loading Screen
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
  },
  loadingLogo: {
    fontSize: 64,
    marginBottom: 16,
  },
  loadingTitle: {
    fontSize: 32,
    fontWeight: '700',
    color: '#135bec',
    marginBottom: 24,
  },
  spinner: {
    marginTop: 16,
  },
});
