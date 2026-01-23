PROPOSTA DE VISUAL DA TELA DE LOGIN:
```html

<!DOCTYPE html>

<html class="light" lang="pt-BR"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Login de Usuário - CNH App</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "primary": "#135bec",
                        "background-light": "#f6f6f8",
                        "background-dark": "#101622",
                    },
                    fontFamily: {
                        "display": ["Public Sans", "sans-serif"]
                    },
                    borderRadius: {
                        "DEFAULT": "0.25rem",
                        "lg": "0.5rem",
                        "xl": "0.75rem",
                        "full": "9999px"
                    },
                },
            },
        }
    </script>
<style>
        body {
            font-family: 'Public Sans', sans-serif;
        }
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
    </style>
<style>
    body {
      min-height: max(884px, 100dvh);
    }
  </style>
  </head>
<body class="bg-background-light dark:bg-background-dark min-h-screen">
<div class="relative flex h-auto min-h-screen w-full max-w-[480px] mx-auto flex-col bg-white dark:bg-background-dark overflow-x-hidden shadow-xl">
<!-- TopAppBar -->
<div class="flex items-center bg-white dark:bg-background-dark p-4 pb-2 justify-between">
<div class="text-[#111318] dark:text-white flex size-12 shrink-0 items-center justify-start cursor-pointer">
<span class="material-symbols-outlined">arrow_back_ios</span>
</div>
<h2 class="text-[#111318] dark:text-white text-lg font-bold leading-tight tracking-[-0.015em] flex-1 text-center pr-12">Login</h2>
</div>
<!-- HeaderImage / Illustration Section -->
<div class="px-4 py-6">
<div class="w-full bg-primary/10 rounded-xl flex items-center justify-center min-h-[180px] border border-primary/5">
<div class="flex flex-col items-center gap-3">
<div class="bg-primary p-4 rounded-full shadow-lg shadow-primary/30">
<span class="material-symbols-outlined text-white !text-5xl">directions_car</span>
</div>
<div class="text-primary font-bold text-xl">AutoEscola Digital</div>
</div>
</div>
</div>
<!-- Headline & Body Text -->
<div class="px-4">
<h1 class="text-[#111318] dark:text-white tracking-light text-[32px] font-bold leading-tight text-left">Bem-vindo de volta!</h1>
<p class="text-[#616f89] dark:text-gray-400 text-base font-normal leading-normal pt-1">Pronto para sua próxima aula de direção?</p>
</div>
<!-- Form Fields -->
<div class="flex flex-col gap-2 px-4 py-6">
<!-- Email Field -->
<div class="flex flex-col w-full">
<p class="text-[#111318] dark:text-white text-sm font-semibold leading-normal pb-2">E-mail</p>
<div class="relative group">
<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
<span class="material-symbols-outlined text-gray-400 group-focus-within:text-primary">mail</span>
</div>
<input class="form-input flex w-full rounded-lg text-[#111318] dark:text-white dark:bg-[#1a212f] focus:outline-0 focus:ring-1 focus:ring-primary border border-[#dbdfe6] dark:border-gray-700 bg-white h-14 placeholder:text-[#616f89] pl-10 pr-4 text-base font-normal shadow-sm" placeholder="exemplo@email.com" type="email" value=""/>
</div>
</div>
<!-- Password Field -->
<div class="flex flex-col w-full mt-2">
<div class="flex justify-between items-center pb-2">
<p class="text-[#111318] dark:text-white text-sm font-semibold leading-normal">Senha</p>
<a class="text-primary text-sm font-medium hover:underline" href="#">Esqueceu a senha?</a>
</div>
<div class="relative group">
<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
<span class="material-symbols-outlined text-gray-400 group-focus-within:text-primary">lock</span>
</div>
<input class="form-input flex w-full rounded-lg text-[#111318] dark:text-white dark:bg-[#1a212f] focus:outline-0 focus:ring-1 focus:ring-primary border border-[#dbdfe6] dark:border-gray-700 bg-white h-14 placeholder:text-[#616f89] pl-10 pr-12 text-base font-normal shadow-sm" placeholder="••••••••" type="password" value=""/>
<div class="absolute inset-y-0 right-0 pr-3 flex items-center cursor-pointer">
<span class="material-symbols-outlined text-gray-400">visibility</span>
</div>
</div>
</div>
</div>
<!-- Login Button -->
<div class="px-4 py-2">
<button class="w-full bg-primary text-white font-bold py-4 rounded-xl shadow-lg shadow-primary/25 hover:bg-primary/90 transition-colors active:scale-[0.98]">
                Entrar
            </button>
</div>
<!-- Social Login Divider -->
<div class="flex items-center px-4 py-8">
<div class="flex-grow border-t border-gray-200 dark:border-gray-700"></div>
<span class="px-4 text-gray-400 text-sm">Ou entre com</span>
<div class="flex-grow border-t border-gray-200 dark:border-gray-700"></div>
</div>
<!-- Social Icons -->
<div class="flex justify-center gap-6 px-4">
<button class="flex items-center justify-center w-14 h-14 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
<svg class="w-6 h-6" viewbox="0 0 24 24">
<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"></path>
<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 12-4.53z" fill="#EA4335"></path>
</svg>
</button>
<button class="flex items-center justify-center w-14 h-14 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
<svg class="w-6 h-6 dark:fill-white" fill="black" viewbox="0 0 24 24">
<path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.11.78.93-.11 2.1-.86 3.62-.69 1.44.1 2.59.73 3.23 1.76-2.9 1.76-2.44 5.92.51 7.15-.6 1.64-1.38 3.19-2.47 3.97zM12.03 7.25c-.14-2.18 1.63-4.09 3.61-4.25.26 2.45-2.22 4.41-3.61 4.25z"></path>
</svg>
</button>
</div>
<!-- Create Account Link -->
<div class="mt-auto py-10 text-center">
<p class="text-gray-500 dark:text-gray-400">Não tem uma conta? 
                <a class="text-primary font-bold hover:underline" href="#">Criar conta</a>
</p>
</div>
<!-- iOS Safe Area Spacer -->
<div class="h-8 bg-white dark:bg-background-dark"></div>
</div>
</body></html>
```

![[screen.png]]