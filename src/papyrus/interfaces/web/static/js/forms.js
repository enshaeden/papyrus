document.addEventListener("DOMContentLoaded", () => {
  const title = document.querySelector("#title");
  const objectId = document.querySelector("#object_id");
  const canonicalPath = document.querySelector("#canonical_path");
  const objectType = document.querySelector("#object_type");
  if (!title || !objectId || !canonicalPath || !objectType) return;
  const slugify = (value) =>
    value
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .replace(/-{2,}/g, "-");
  const suggest = () => {
    const slug = slugify(title.value);
    if (!slug) return;
    if (!objectId.value) objectId.value = `kb-${slug}`;
    if (!canonicalPath.value) canonicalPath.value = `knowledge/${objectType.value.replace("_", "-")}s/${slug}.md`;
  };
  title.addEventListener("blur", suggest);
  objectType.addEventListener("change", suggest);
});
