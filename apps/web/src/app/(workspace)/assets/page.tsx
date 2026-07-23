"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CopyCheck, FileArchive, HardDriveUpload, ShieldCheck } from "lucide-react";
import { FormEvent, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { Asset } from "@/lib/contracts";

export default function AssetsPage() {
  const queryClient = useQueryClient();
  const assets = useQuery({ queryKey: ["assets"], queryFn: api.assets });
  const [file, setFile] = useState<File | null>(null);
  const [rights, setRights] = useState<Asset["rights_status"]>("unknown");
  const [rightsNotes, setRightsNotes] = useState("");
  const [tags, setTags] = useState("");

  const upload = useMutation({
    mutationFn: api.uploadAsset,
    onSuccess: async () => {
      setFile(null);
      setRightsNotes("");
      setTags("");
      await queryClient.invalidateQueries({ queryKey: ["assets"] });
    },
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.set("file", file);
    formData.set("rights_status", rights);
    formData.set("rights_notes", rightsNotes);
    formData.set("tags", tags);
    upload.mutate(formData);
  };

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Asset management · Originals preserved"
        title="Know what every file is, where it came from, and whether it can be used."
        description="Uploads are checksummed, deduplicated, stored behind the API, and assigned an explicit rights state. Unknown rights remain unknown—BrandOS never invents permission."
        actions={<StatusPill tone="blue">{assets.data?.length ?? 0} assets</StatusPill>}
      />

      {assets.isPending && <LoadingGrid />}
      {assets.error && (
        <ErrorState error={assets.error} retry={() => void assets.refetch()} />
      )}

      {!assets.isPending && !assets.error && (
        <section className="grid gap-5 xl:grid-cols-[22rem_minmax(0,1fr)]">
          <form className="surface h-fit p-5" onSubmit={submit}>
            <div className="flex items-center justify-between">
              <div>
                <p className="eyebrow">Ingest original</p>
                <h2 className="mt-2 text-lg font-semibold">Add an asset safely</h2>
              </div>
              <HardDriveUpload className="size-5 text-gold" />
            </div>
            <label className="mt-5 block">
              <span className="mb-2 block text-xs font-semibold text-muted">File</span>
              <input
                className="input file:mr-3 file:rounded-md file:border-0 file:bg-gold/10 file:px-2 file:py-1 file:text-xs file:text-gold"
                type="file"
                required
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <label className="mt-4 block">
              <span className="mb-2 block text-xs font-semibold text-muted">Rights status</span>
              <select
                className="input"
                value={rights}
                onChange={(event) =>
                  setRights(event.target.value as Asset["rights_status"])
                }
              >
                <option value="unknown">Unknown</option>
                <option value="owned">Owned</option>
                <option value="licensed">Licensed</option>
                <option value="restricted">Restricted</option>
              </select>
            </label>
            <label className="mt-4 block">
              <span className="mb-2 block text-xs font-semibold text-muted">
                Rights notes
              </span>
              <textarea
                className="input min-h-24 resize-y"
                value={rightsNotes}
                placeholder="Creator, license, expiry, or why rights are unknown"
                onChange={(event) => setRightsNotes(event.target.value)}
              />
            </label>
            <label className="mt-4 block">
              <span className="mb-2 block text-xs font-semibold text-muted">
                Tags · comma separated
              </span>
              <input
                className="input"
                value={tags}
                placeholder="founder, studio, vertical"
                onChange={(event) => setTags(event.target.value)}
              />
            </label>
            <button
              className="button-primary mt-5 w-full"
              type="submit"
              disabled={!file || upload.isPending}
            >
              <HardDriveUpload className="size-4" />
              Preserve and index
            </button>
            {upload.isError && (
              <p className="mt-3 text-xs text-danger">{upload.error.message}</p>
            )}
          </form>

          <div className="surface p-5">
            <p className="eyebrow">Asset library</p>
            <div className="mt-5 grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
              {assets.data?.map((asset) => (
                <article key={asset.id} className="rounded-xl border border-line p-4">
                  <div className="flex items-start justify-between gap-3">
                    <span className="grid size-10 shrink-0 place-items-center rounded-xl border border-line bg-canvas/55">
                      <FileArchive className="size-5 text-blue" />
                    </span>
                    <div className="flex flex-wrap justify-end gap-1.5">
                      <StatusPill
                        tone={
                          asset.rights_status === "owned" ||
                          asset.rights_status === "licensed"
                            ? "green"
                            : asset.rights_status === "restricted"
                              ? "danger"
                              : "gold"
                        }
                      >
                        {asset.rights_status}
                      </StatusPill>
                      {asset.is_demo && <StatusPill>Demo</StatusPill>}
                    </div>
                  </div>
                  <h2 className="mt-4 truncate text-sm font-semibold" title={asset.filename}>
                    {asset.filename}
                  </h2>
                  <p className="mt-2 text-[0.65rem] text-faint">
                    {asset.mime_type} · {formatBytes(asset.size_bytes)}
                  </p>
                  <div className="mt-4 flex flex-wrap gap-1.5">
                    {asset.tags.map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full border border-line px-2 py-1 text-[0.6rem] text-muted"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="mt-4 border-t border-line pt-3">
                    <p className="flex items-center gap-2 text-[0.65rem] text-muted">
                      {asset.original_preserved ? (
                        <ShieldCheck className="size-3.5 text-green" />
                      ) : (
                        <FileArchive className="size-3.5 text-gold" />
                      )}
                      {asset.original_preserved
                        ? "Original preserved"
                        : "Metadata-only demo record"}
                    </p>
                    {asset.duplicate_of_id && (
                      <p className="mt-2 flex items-center gap-2 text-[0.65rem] text-purple">
                        <CopyCheck className="size-3.5" />
                        Duplicate linked to original record
                      </p>
                    )}
                    <p className="mt-2 truncate font-mono text-[0.58rem] text-faint">
                      SHA-256 {asset.checksum_sha256}
                    </p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

function formatBytes(value: number) {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}
