let lunrIndex;
let searchData = [];

window.initPageScripts = async function () {
    // --- Поиск ---
    try {
        const res = await fetch(window.__BASE_PATH__ + "search-index.json");
        searchData = await res.json();

        lunrIndex = lunr(function () {
            this.use(lunr.ru);
            this.ref("url");
            this.field("title");
            this.field("keywords");

            searchData.forEach(doc => {
                this.add({
                    url: doc.url,
                    title: doc.title,
                    keywords: Array.isArray(doc.keywords) ? doc.keywords.join(" ") : ""
                });
            });
        });

        const input = document.getElementById("search-input");
        const resultsList = document.getElementById("search-results");

        if (input && resultsList) {
            input.addEventListener("input", () => {
                const query = input.value.trim();
                resultsList.innerHTML = "";
                if (!query) {
                    resultsList.style.display = "none";
                    return;
                }

                const results = lunrIndex.search(query);
                if (results.length === 0) {
                    resultsList.innerHTML = "<li>Ничего не найдено</li>";
                    resultsList.style.display = "block";
                    return;
                }

                for (const result of results) {
                    const page = searchData.find(d => d.url === result.ref);
                    const item = document.createElement("li");
                    const link = document.createElement("a");
                    link.href = window.__BASE_PATH__ + page.url;
                    link.textContent = page.title;
                    item.appendChild(link);
                    resultsList.appendChild(item);
                }

                resultsList.style.display = "block";
            });
        }

    } catch (err) {
        console.error("Ошибка загрузки search-index.json", err);
    }

    // --- Вкладки ---
    document.querySelectorAll(".tab-buttons").forEach(tabGroup => {
        const buttons = tabGroup.querySelectorAll(".tab-button");

        buttons.forEach(button => {
            button.addEventListener("click", (e) => {
                e.preventDefault();
                const targetId = button.getAttribute("data-tab");
                const container = tabGroup.parentElement;

                buttons.forEach(b => b.classList.remove("active"));
                button.classList.add("active");

                container.querySelectorAll(".tab-content").forEach(div => {
                    div.style.display = div.id === targetId ? "block" : "none";
                });
            });
        });
    });

    // --- Кнопка "Наверх" ---
    const scrollBtn = document.getElementById("scrollToTopBtn");
    const footer = document.querySelector(".custom-footer")
    if (scrollBtn && !footer) {
        window.addEventListener("scroll", () => {
            scrollBtn.style.display = window.scrollY > 300 ? "block" : "none";
        });

        scrollBtn.addEventListener("click", () => {
            window.scrollTo({top: 0, behavior: "smooth"});
        });
    }

    // --- Оглавление ---
    const tocToggle = document.getElementById("toc-toggle");
    const tocPopup = document.getElementById("toc-popup");
    const tocDynamic = document.getElementById("toc-dynamic");
    const pageToc = document.querySelector(".page-toc");

    if (tocToggle && tocPopup && tocDynamic) {
        if (pageToc) {
            tocDynamic.innerHTML = pageToc.innerHTML;
        } else {
            tocDynamic.innerHTML = "";
        }

        tocToggle.onclick = () => {
            tocPopup.classList.toggle("hidden");
        };

        window.addEventListener("scroll", () => {
            if (window.scrollY > 200 && tocDynamic.innerHTML.trim()) {
                tocToggle.style.display = "block";
            } else {
                tocToggle.style.display = "none";
                tocPopup.classList.add("hidden");
            }
        });
    }

    // --- Включение фавайкона ---
    function ensureFavicon() {
        const faviconHref = (window.__BASE_PATH__ || '/data-pool' + '/') + 'images/favicon.png';
        const existing = document.querySelector("link[rel='icon']");

        if (!existing || existing.href !== location.origin + faviconHref) {
            if (existing) existing.remove();

            const link = document.createElement("link");
            link.rel = "icon";
            link.href = faviconHref;
            link.type = "image/png";
            document.head.appendChild(link);
        }
    }

    // --- Вкладки разделов ---
    const tabs = document.querySelectorAll(".page-tab-item");
    const gmScreen = document.getElementById("gm-screen-mode");
    const enemies = document.getElementById("enemies-mode")
    //const charlist = document.getElementById("charlist")
    const site = document.getElementById("main-content");
    const sidebar = document.getElementById("sidebar");
    let gmInitialized = false;
    tabs.forEach(tab => {
        tab.addEventListener("click", async (event) => {
            const id = event.currentTarget.dataset.open;
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            console.log("clicked: " + id)

            //todo убрать костыли
            switch (id) {
                case "home":
                    gmScreen.classList.remove("active")
                    enemies.classList.remove("active")
                    //charlist.classList.remove("active")
                    site.style.display = ""
                    sidebar.style.display = ""
                    break;
                case "gm-screen":
                    site.style.display = "none";
                    sidebar.style.display = "none";
                    gmScreen.classList.add("active");
                    enemies.classList.remove("active")
                    //charlist.classList.remove("active")
                    if (!gmInitialized) {
                        await loadGMScreen();
                        gmInitialized = true;
                    }
                    break;
                case "enemies":
                    site.style.display = "none"
                    sidebar.style.display = "none"
                    gmScreen.classList.remove("active")
                    //charlist.classList.remove("active")
                    enemies.classList.add("active")
                    await initEnemiesModule()
                    break;
                // case "charlist":
                //     site.style.display = "none"
                //     sidebar.style.display = "none"
                //     gmScreen.classList.remove("active")
                //     enemies.classList.remove("active")
                //     charlist.classList.add("active")
                //     //todo initModule
                //     break;
            }
        });
    });
};

document.addEventListener("DOMContentLoaded", () => {
    initPageScripts();
});

/* ============================================================
   Мобильная версия Data Pool.
   Общий скрипт сайта: создаёт кнопку-гамбургер, боковое
   меню-шторку, а также оборачивает таблицы в прокручиваемые
   контейнеры.  Идемпотентен: повторный запуск ничего не ломает.
   ============================================================ */
(function () {
    "use strict";

    if (window.__dpMobileInstalled) return;
    window.__dpMobileInstalled = true;

    const mobileQuery = window.matchMedia("(max-width: 980px)");
    let setMenuOpen = null;

    function installMenu() {
        const header = document.querySelector(".site-header");
        const sidebar = document.querySelector(".sidebar");
        if (!header && !sidebar) return;

        let button = document.querySelector(".dp-menu-button");
        if (!button && header) {
            button = document.createElement("button");
            button.type = "button";
            button.className = "dp-menu-button";
            button.setAttribute("aria-label", "Открыть меню");
            button.setAttribute("aria-expanded", "false");
            if (sidebar) {
                button.setAttribute("aria-controls", sidebar.id || "sidebar");
            }
            button.innerHTML = "&#9776;";
            header.insertBefore(button, header.firstChild);
        }

        let closeButton = document.querySelector(".dp-menu-close");
        if (!closeButton && sidebar) {
            closeButton = document.createElement("button");
            closeButton.type = "button";
            closeButton.className = "dp-menu-close";
            closeButton.setAttribute("aria-label", "Закрыть меню");
            closeButton.innerHTML = "&times;";
            sidebar.insertBefore(closeButton, sidebar.firstChild);
        }

        let backdrop = document.querySelector(".dp-menu-backdrop");
        if (!backdrop) {
            backdrop = document.createElement("div");
            backdrop.className = "dp-menu-backdrop";
            backdrop.setAttribute("aria-hidden", "true");
            document.body.appendChild(backdrop);
        }

        setMenuOpen = function (open) {
            document.documentElement.classList.toggle("dp-menu-open", open);
            document.body.classList.toggle("dp-menu-open", open);
            if (button) {
                button.setAttribute("aria-expanded", open ? "true" : "false");
            }
        };

        if (button) {
            button.addEventListener("click", () => {
                if (!mobileQuery.matches) return;
                setMenuOpen(!document.body.classList.contains("dp-menu-open"));
            });
        }
        if (closeButton) {
            closeButton.addEventListener("click", () => setMenuOpen(false));
        }
        if (backdrop) {
            backdrop.addEventListener("click", () => setMenuOpen(false));
        }
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" || event.key === "Esc") setMenuOpen(false);
        });
        if (sidebar) {
            sidebar.addEventListener("click", (event) => {
                const link = event.target && event.target.closest
                    ? event.target.closest("a")
                    : null;
                if (link) setMenuOpen(false);
            });
        }

        const handleViewportChange = () => {
            if (!mobileQuery.matches) setMenuOpen(false);
        };
        window.addEventListener("resize", handleViewportChange);
        if (mobileQuery.addEventListener) {
            mobileQuery.addEventListener("change", handleViewportChange);
        } else if (mobileQuery.addListener) {
            mobileQuery.addListener(handleViewportChange);
        }

        syncSpecialMode();
    }

    // В режимах «Ширма Мастера» / «Противники» прячем гамбургер и поиск:
    // навигация там всё равно недоступна (сайдбар скрыт самим сайтом).
    function syncSpecialMode() {
        const gmScreen = document.getElementById("gm-screen-mode");
        const enemies = document.getElementById("enemies-mode");
        const special = !!(gmScreen && gmScreen.classList.contains("active")) ||
            !!(enemies && enemies.classList.contains("active"));
        document.body.classList.toggle("dp-special-mode", special);
        if (special && setMenuOpen) setMenuOpen(false);
    }

    function watchModes() {
        [document.getElementById("gm-screen-mode"), document.getElementById("enemies-mode")]
            .forEach((mode) => {
                if (!mode) return;
                new MutationObserver(syncSpecialMode).observe(mode, {
                    attributes: true,
                    attributeFilter: ["class", "style"]
                });
            });
    }

    function countColumns(table) {
        const row = table.tHead && table.tHead.rows[0]
            ? table.tHead.rows[0]
            : table.rows[0];
        if (!row) return 0;
        let columns = 0;
        for (let i = 0; i < row.cells.length; i += 1) {
            columns += row.cells[i].colSpan || 1;
        }
        return columns;
    }

    // Широкие таблицы на телефоне прокручиваются горизонтально,
    // остальные просто сжимаются по ширине экрана.
    function wrapTables() {
        const tables = document.querySelectorAll("table");
        for (let i = 0; i < tables.length; i += 1) {
            const table = tables[i];
            if (table.closest(".table-scroll")) continue;
            if (table.closest(".sidebar") || table.closest(".toc-popup")) continue;
            const wrapper = document.createElement("div");
            wrapper.className = countColumns(table) >= 4
                ? "table-scroll table-scroll-wide"
                : "table-scroll";
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    }

    let wrapScheduled = false;
    function scheduleWrapTables() {
        if (wrapScheduled) return;
        wrapScheduled = true;
        window.setTimeout(() => {
            wrapScheduled = false;
            wrapTables();
        }, 60);
    }

    function watchContent() {
        ["main-content", "gm-screen-content", "enemy-details"].forEach((id) => {
            const container = document.getElementById(id);
            if (!container) return;
            new MutationObserver(scheduleWrapTables).observe(container, {
                childList: true,
                subtree: true
            });
        });
    }

    // spa.js перезаписывает #main-content и вызывает initPageScripts —
    // после каждого перехода оборачиваем новые таблицы.
    const originalInit = window.initPageScripts;
    if (typeof originalInit === "function") {
        window.initPageScripts = function () {
            const result = originalInit.apply(this, arguments);
            scheduleWrapTables();
            return result;
        };
    }

    function init() {
        installMenu();
        watchModes();
        watchContent();
        wrapTables();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
