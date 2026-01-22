/**
 * GoDrive Mobile - Main App Entry
 *
 * Configuração do QueryClientProvider e providers globais.
 */

import React from 'react';
import { SafeAreaView, StyleSheet, Text, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './src/lib/queryClient';
import { Button } from './src/shared/components';

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SafeAreaView style={styles.container}>
        <StatusBar style="auto" />

        <View style={styles.content}>
          <Text style={styles.logo}>🚗</Text>
          <Text style={styles.title}>GoDrive</Text>
          <Text style={styles.subtitle}>
            Conectando alunos a instrutores de direção
          </Text>

          <View style={styles.buttonContainer}>
            <Button
              title="Começar"
              onPress={() => {
                // Navegação será implementada na Fase 2
              }}
              size="lg"
              fullWidth
            />

            <Button
              title="Já tenho conta"
              onPress={() => {
                // Navegação será implementada na Fase 2
              }}
              variant="outline"
              size="lg"
              fullWidth
              style={styles.secondaryButton}
            />
          </View>
        </View>

        <Text style={styles.version}>v1.0.0 - Fase 1</Text>
      </SafeAreaView>
    </QueryClientProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f9ff',
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },
  logo: {
    fontSize: 80,
    marginBottom: 16,
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#0c4a6e',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#075985',
    textAlign: 'center',
    marginBottom: 48,
  },
  buttonContainer: {
    width: '100%',
    gap: 16,
  },
  secondaryButton: {
    marginTop: 8,
  },
  version: {
    textAlign: 'center',
    color: '#64748b',
    paddingBottom: 24,
    fontSize: 12,
  },
});
