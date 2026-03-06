import { NextResponse, type NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
    const token = request.cookies.get('admin_access_token')?.value || '';
    const { pathname } = request.nextUrl;

    // Se estiver tentando acessar o login já autenticado, redireciona para home
    if (pathname === '/login' && token) {
        return NextResponse.redirect(new URL('/', request.url));
    }

    // Se não estiver autenticado e não for a página de login nem arquivos públicos/estáticos
    if (!token && pathname !== '/login' && !pathname.startsWith('/_next') && !pathname.includes('.')) {
        return NextResponse.redirect(new URL('/login', request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
