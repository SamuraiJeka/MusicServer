import styles from "./MediaGrid.module.scss";

const FALLBACK_COVER = "src/static/picture.png";

function formatReleaseDate(value) {
  if (!value) return "";
  try {
    const d = value instanceof Date ? value : new Date(value);
    if (Number.isNaN(d.getTime())) return "";
    return d.toLocaleDateString("ru-RU", { year: "numeric", month: "2-digit", day: "2-digit" });
  } catch {
    return "";
  }
}

export default function MediaGrid({
  title,
  items = [],
  emptyText = "Пока пусто.",
  getCoverSrc = (item) => item?.cover_url || item?.image_url || item?.img || FALLBACK_COVER,
  getTitle = (item) => item?.title ?? "",
  getAuthor = (item) => item?.author ?? item?.artist ?? "",
  // Date is optional and should be explicitly provided by callers
  // (e.g. for albums, but not for playlists).
  getReleaseDate = () => null,
  onItemClick,
}) {
  const safeItems = Array.isArray(items) ? items : [];

  return (
    <div className={styles.wrapper}>
      {title ? <div className={styles.header}>{title}</div> : null}

      {safeItems.length === 0 ? (
        <div className={styles.empty}>{emptyText}</div>
      ) : (
        <div className={styles.grid}>
          {safeItems.map((item) => {
            const key = item?.id ?? `${getTitle(item)}-${getAuthor(item)}`;
            const cover = getCoverSrc(item) || FALLBACK_COVER;
            const name = getTitle(item);
            const author = getAuthor(item);
            const dateText = formatReleaseDate(getReleaseDate(item));

            return (
              <button
                key={String(key)}
                type="button"
                className={styles.card}
                onClick={onItemClick ? () => onItemClick(item) : undefined}
              >
                <div className={styles.cover}>
                  <img src={cover} alt="" />
                </div>
                <div className={styles.meta}>
                  <div className={styles.name} title={name}>
                    {name}
                  </div>
                  <div className={styles.metaRow}>
                    <div className={styles.author} title={author}>
                      {author}
                    </div>
                    {dateText ? <div className={styles.date}>{dateText}</div> : null}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

