import { getOrCreateUser } from "@/lib/get-or-create-user";
import { DisplayNameForm } from "@/components/display-name-form";

export default async function ProfilePage() {
  const user = await getOrCreateUser();
  if (!user) {
    return <p className="text-slate-400">Bu sayfayı görmek için giriş yapmalısınız.</p>;
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Profil</h1>
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
        <DisplayNameForm initialName={user.displayName} />
      </div>
    </div>
  );
}
