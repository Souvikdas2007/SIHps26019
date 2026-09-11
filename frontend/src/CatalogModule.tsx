import { FormEvent, RefObject, useEffect, useState } from "react";

type DatasetVersion = {
  id: number;
  version: string;
  data_year: number | null;
  crs: string | null;
  asset_path: string;
  checksum: string | null;
};

type Dataset = {
  id: number;
  profile_identifier: string;
  name: string;
  source: string;
  versions: DatasetVersion[];
};

type Model = {
  id: number;
  provider: string;
  runtime: string;
  model_name: string;
  model_version: string;
  model_format: string;
  asset_path: string | null;
  checksum: string | null;
};

type Catalog = { datasets: Dataset[]; models: Model[] };

type CatalogModuleProps = {
  api: string;
  token: string;
  onToast: (message: string) => void;
  sectionRef: RefObject<HTMLElement | null>;
};

const emptyDataset = {
  profile_identifier: "",
  version: "v1",
  display_name: "",
  source: "",
  source_url: "",
  data_year: "2024",
  crs: "EPSG:4326",
  asset_path: "data/processed/",
  region_identifier: "",
  region_version: "v1",
  region_display_name: "",
};

const emptyModel = {
  provider: "local",
  runtime: "llama.cpp",
  model_name: "",
  model_version: "v1",
  model_format: "gguf",
  asset_path: "",
  checksum: "",
};

export function CatalogModule({ api, token, onToast, sectionRef }: CatalogModuleProps) {
  const [catalog, setCatalog] = useState<Catalog>({ datasets: [], models: [] });
  const [datasetForm, setDatasetForm] = useState(emptyDataset);
  const [modelForm, setModelForm] = useState(emptyModel);
  const [catalogError, setCatalogError] = useState("");
  const [catalogBusy, setCatalogBusy] = useState(false);

  async function loadCatalog() {
    if (!token) {
      setCatalogError("Log in to manage local datasets and models.");
      return;
    }
    setCatalogBusy(true);
    setCatalogError("");
    try {
      const response = await fetch(`${api}/api/catalog`, { headers: { Authorization: `Bearer ${token}` } });
      if (!response.ok) throw new Error(`Catalog request failed (${response.status})`);
      setCatalog(await response.json());
    } catch (error) {
      setCatalogError(error instanceof Error ? error.message : "Catalog request failed");
    } finally {
      setCatalogBusy(false);
    }
  }

  useEffect(() => {
    void loadCatalog();
  }, [token]);

  async function registerDataset(event: FormEvent) {
    event.preventDefault();
    await registerAsset("/api/catalog/datasets", datasetForm, "Dataset registered", () => setDatasetForm(emptyDataset));
  }

  async function registerModel(event: FormEvent) {
    event.preventDefault();
    await registerAsset("/api/catalog/models", {
      ...modelForm,
      asset_path: modelForm.asset_path || null,
      checksum: modelForm.checksum || null,
    }, "Model registered", () => setModelForm(emptyModel));
  }

  async function registerAsset(path: string, body: object, successMessage: string, reset: () => void) {
    setCatalogBusy(true);
    setCatalogError("");
    try {
      const response = await fetch(`${api}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(body),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.detail ?? `Registration failed (${response.status})`);
      reset();
      await loadCatalog();
      onToast(successMessage);
    } catch (error) {
      setCatalogError(error instanceof Error ? error.message : "Registration failed");
    } finally {
      setCatalogBusy(false);
    }
  }

  const updateDataset = (key: keyof typeof emptyDataset, value: string) => setDatasetForm((previous) => ({ ...previous, [key]: value }));
  const updateModel = (key: keyof typeof emptyModel, value: string) => setModelForm((previous) => ({ ...previous, [key]: value }));

  return (
    <section className="catalog-module section-anchor" id="catalog" data-section="Catalog" ref={sectionRef}>
      <div className="catalog-heading">
        <div><span className="catalog-kicker">05 / Catalog</span><h2>Plug in local assets</h2><p>Register versioned LULC datasets and local models without changing the analysis workflow.</p></div>
        <button className="catalog-refresh" onClick={() => void loadCatalog()} disabled={catalogBusy}>Refresh catalog</button>
      </div>
      {catalogError && <p className="catalog-error" role="alert">{catalogError}</p>}
      {!token && <p className="catalog-empty">Authenticate as an admin or researcher to view and manage the local catalog.</p>}
      {token && <>
        <div className="catalog-inventory">
          <div className="inventory-block"><div className="inventory-title"><strong>Datasets</strong><span>{catalog.datasets.length}</span></div>{catalog.datasets.length === 0 ? <p className="catalog-empty">No datasets registered.</p> : catalog.datasets.map((dataset) => <div className="asset-row" key={dataset.id}><div><strong>{dataset.name}</strong><small>{dataset.profile_identifier} · {dataset.source}</small></div><span>{dataset.versions.length} version{dataset.versions.length === 1 ? "" : "s"}</span>{dataset.versions.map((version) => <small className="asset-version" key={version.id}>{version.version} · {version.data_year ?? "year n/a"} · {version.crs ?? "CRS n/a"}</small>)}</div>)}</div>
          <div className="inventory-block"><div className="inventory-title"><strong>Models</strong><span>{catalog.models.length}</span></div>{catalog.models.length === 0 ? <p className="catalog-empty">No models registered.</p> : catalog.models.map((model) => <div className="asset-row" key={model.id}><div><strong>{model.model_name}</strong><small>{model.provider} · {model.runtime}</small></div><span>{model.model_format}</span><small className="asset-version">{model.model_version}{model.asset_path ? ` · ${model.asset_path}` : " · metadata only"}</small></div>)}</div>
        </div>
        <div className="catalog-forms">
          <form className="asset-form" onSubmit={(event) => void registerDataset(event)}><div className="form-title"><strong>Add LULC dataset</strong><small>Existing local GeoJSON only</small></div><div className="form-grid"><input required placeholder="Display name" value={datasetForm.display_name} onChange={(event) => updateDataset("display_name", event.target.value)} /><input required placeholder="Profile ID e.g. bengal-lulc" value={datasetForm.profile_identifier} onChange={(event) => updateDataset("profile_identifier", event.target.value)} /><input required placeholder="Source" value={datasetForm.source} onChange={(event) => updateDataset("source", event.target.value)} /><input required placeholder="Asset path: data/processed/file.geojson" value={datasetForm.asset_path} onChange={(event) => updateDataset("asset_path", event.target.value)} /><input required placeholder="Region ID" value={datasetForm.region_identifier} onChange={(event) => updateDataset("region_identifier", event.target.value)} /><input required placeholder="Region display name" value={datasetForm.region_display_name} onChange={(event) => updateDataset("region_display_name", event.target.value)} /><input placeholder="Version" value={datasetForm.version} onChange={(event) => updateDataset("version", event.target.value)} /><input placeholder="Data year" type="number" value={datasetForm.data_year} onChange={(event) => updateDataset("data_year", event.target.value)} /></div><button disabled={catalogBusy}>Register dataset</button></form>
          <form className="asset-form" onSubmit={(event) => void registerModel(event)}><div className="form-title"><strong>Add local model</strong><small>GGUF metadata and path</small></div><div className="form-grid"><input required placeholder="Model name" value={modelForm.model_name} onChange={(event) => updateModel("model_name", event.target.value)} /><input required placeholder="Asset path: models/local/model.gguf" value={modelForm.asset_path} onChange={(event) => updateModel("asset_path", event.target.value)} /><input placeholder="Provider" value={modelForm.provider} onChange={(event) => updateModel("provider", event.target.value)} /><input placeholder="Runtime" value={modelForm.runtime} onChange={(event) => updateModel("runtime", event.target.value)} /><input placeholder="Version" value={modelForm.model_version} onChange={(event) => updateModel("model_version", event.target.value)} /><input placeholder="Format" value={modelForm.model_format} onChange={(event) => updateModel("model_format", event.target.value)} /></div><button disabled={catalogBusy}>Register model</button></form>
        </div>
      </>}
    </section>
  );
}
