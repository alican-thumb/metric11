import Link from "next/link";
import { Show, SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";

export function NavBar() {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-10">
      <div className="mx-auto flex max-w-4xl items-center justify-between gap-4 px-4 py-3">
        <div className="flex items-center gap-3">
          <a href="https://metric11.com" className="text-xs text-slate-500 hover:text-slate-300">
            ← metric11.com
          </a>
          <Link href="/" className="flex items-center gap-2 font-bold text-lg">
            <span className="grid h-7 w-7 place-items-center rounded-md bg-lime-300 text-slate-900 text-sm">
              11
            </span>
            metric11 <span className="text-lime-300">Tahmin</span>
          </Link>
        </div>
        <nav className="flex flex-wrap items-center justify-end gap-x-4 gap-y-1 text-sm">
          <Link href="/" className="text-slate-300 hover:text-white">
            Bu Hafta
          </Link>
          <Show when="signed-in">
            <Link href="/predictions" className="text-slate-300 hover:text-white">
              Tahminlerim
            </Link>
          </Show>
          <Link href="/topluluk" className="text-slate-300 hover:text-white">
            Topluluk Tahminleri
          </Link>
          <Link href="/leaderboard" className="text-slate-300 hover:text-white">
            Lider Tablosu
          </Link>
          <Show when="signed-out">
            <SignInButton mode="modal">
              <button className="cursor-pointer text-slate-300 hover:text-white">Giriş Yap</button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="cursor-pointer rounded-md bg-lime-300 px-3 py-1.5 font-semibold text-slate-900">
                Üye Ol
              </button>
            </SignUpButton>
          </Show>
          <Show when="signed-in">
            <UserButton>
              <UserButton.MenuItems>
                <UserButton.Link label="Kullanıcı Adı" href="/profil" labelIcon={<span>✏️</span>} />
              </UserButton.MenuItems>
            </UserButton>
          </Show>
        </nav>
      </div>
    </header>
  );
}
