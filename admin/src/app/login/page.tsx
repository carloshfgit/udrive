'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle } from 'lucide-react';

const loginSchema = z.object({
    email: z.string().email('Email inválido'),
    password: z.string().min(6, 'A senha deve ter pelo menos 6 caracteres'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
    const { login, isLoading } = useAuth();
    const [error, setError] = React.useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginFormValues>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginFormValues) => {
        try {
            setError(null);
            await login(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Erro ao fazer login. Verifique suas credenciais.');
        }
    };

    return (
        <div className="flex h-screen w-full items-center justify-center bg-zinc-50 dark:bg-zinc-950 px-4">
            <Card className="w-full max-w-md shadow-lg border-2">
                <CardHeader className="space-y-1 text-center">
                    <div className="flex justify-center mb-4">
                        <div className="h-12 w-12 rounded-xl bg-primary flex items-center justify-center text-primary-foreground font-bold text-2xl">
                            G
                        </div>
                    </div>
                    <CardTitle className="text-2xl font-bold">GoDrive Admin</CardTitle>
                    <CardDescription>
                        Entre com suas credenciais para acessar o painel
                    </CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <CardContent className="space-y-4">
                        {error && (
                            <div className="flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive border border-destructive/20">
                                <AlertCircle size={16} />
                                <span>{error}</span>
                            </div>
                        )}
                        <div className="space-y-2">
                            <label className="text-sm font-medium leading-none" htmlFor="email">
                                Email
                            </label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="admin@godrive.com.br"
                                {...register('email')}
                                className={errors.email ? 'border-destructive' : ''}
                            />
                            {errors.email && (
                                <p className="text-xs text-destructive">{errors.email.message}</p>
                            )}
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium leading-none" htmlFor="password">
                                Senha
                            </label>
                            <Input
                                id="password"
                                type="password"
                                {...register('password')}
                                className={errors.password ? 'border-destructive' : ''}
                            />
                            {errors.password && (
                                <p className="text-xs text-destructive">{errors.password.message}</p>
                            )}
                        </div>
                    </CardContent>
                    <CardFooter>
                        <Button className="w-full h-11" type="submit" disabled={isLoading}>
                            {isLoading ? 'Entrando...' : 'Acessar Painel'}
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
