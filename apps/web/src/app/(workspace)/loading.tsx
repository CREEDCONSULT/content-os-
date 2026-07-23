export default function WorkspaceLoading() {
  return (
    <div className="space-y-6" aria-label="Loading workspace">
      <div>
        <div className="skeleton h-3 w-32 rounded" />
        <div className="skeleton mt-4 h-10 max-w-xl rounded" />
        <div className="skeleton mt-4 h-4 max-w-2xl rounded" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => (
          <div key={index} className="skeleton h-36 rounded-2xl" />
        ))}
      </div>
    </div>
  );
}
