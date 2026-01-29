/**
 * GoDrive Mobile - Main App Entry
 *
 * Configuração do QueryClientProvider, NavigationContainer e providers globais.
 */

import './global.css';
import React, { useEffect } from 'react';
import { StyleSheet, ActivityIndicator, View, Text } from 'react-native';
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

/**
 * Placeholder para o navigator principal (autenticado).
 * Será implementado nas próximas fases.
 */
function MainNavigator() {
  const { logout } = useAuthStore();

  return (
    <View style={styles.mainContainer}>
      <Text style={styles.mainLogo}>🚗</Text>
      <Text style={styles.mainTitle}>GoDrive</Text>
      <Text style={styles.mainSubtitle}>Bem-vindo!</Text>
      <Text style={styles.mainText}>
        Você está autenticado. As demais funcionalidades serão implementadas nas próximas fases.
      </Text>
      <View style={styles.logoutButton}>
        <Text style={styles.logoutButtonText} onPress={logout}>
          Sair
        </Text>
      </View>
    </View>
  );
}

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
            <NavigationContainer>
              {isAuthenticated ? <MainNavigator /> : <AuthNavigator />}
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
  // Main Navigator Placeholder
  mainContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
    paddingHorizontal: 32,
  },
  mainLogo: {
    fontSize: 64,
    marginBottom: 16,
  },
  mainTitle: {
    fontSize: 32,
    fontWeight: '700',
    color: '#135bec',
    marginBottom: 8,
  },
  mainSubtitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#111318',
    marginBottom: 16,
  },
  mainText: {
    fontSize: 16,
    color: '#616f89',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  logoutButton: {
    backgroundColor: '#ef4444',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  logoutButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
});
