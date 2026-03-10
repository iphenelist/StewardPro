(function () {
	const MANIFEST_ID = "stewardpro-pwa-manifest";
	const BANNER_ID = "stewardpro-pwa-banner";
	const DISMISS_KEY = "stewardpro-pwa-dismissed-at";
	const INSTALLED_KEY = "stewardpro-pwa-installed";
	const DISMISS_WINDOW_MS = 7 * 24 * 60 * 60 * 1000;
	const BUILD_VERSION = window._version_number || "dev";
	const APPLE_ICON = "/assets/stewardpro/pwa/icons/apple-touch-icon.png";
	const ICON = "/assets/stewardpro/pwa/icons/stewardpro-icon-192.png";
	const MANIFEST_URL = `/stewardpro-manifest.json?v=${encodeURIComponent(BUILD_VERSION)}`;
	const SW_URL = `/stewardpro-sw.js?v=${encodeURIComponent(BUILD_VERSION)}`;
	const THEME_COLOR = "#0d5c63";
	const APP_ROUTES = ["/app", "/login"];

	let deferredPrompt = null;
	let banner;

	const isRelevantRoute = () =>
		APP_ROUTES.some((route) => window.location.pathname === route || window.location.pathname.startsWith(`${route}/`));

	const isStandalone = () =>
		window.matchMedia?.("(display-mode: standalone)").matches || window.navigator.standalone === true;

	const canShowBanner = () => {
		if (isStandalone() || localStorage.getItem(INSTALLED_KEY)) {
			return false;
		}

		const dismissedAt = Number(localStorage.getItem(DISMISS_KEY) || 0);
		return !dismissedAt || Date.now() - dismissedAt > DISMISS_WINDOW_MS;
	};

	const isSecureOrigin = () =>
		window.isSecureContext || ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);

	const isIOS = () => /iphone|ipad|ipod/i.test(window.navigator.userAgent);

	const isSafari = () => {
		const userAgent = window.navigator.userAgent;
		return /Safari/i.test(userAgent) && !/Chrome|CriOS|EdgiOS|FxiOS/i.test(userAgent);
	};

	const ensureHeadTag = (selector, factory) => {
		let node = document.head.querySelector(selector);
		if (!node) {
			node = factory();
			document.head.appendChild(node);
		}
		return node;
	};

	const injectPwaMeta = () => {
		ensureHeadTag(`#${MANIFEST_ID}`, () => {
			const link = document.createElement("link");
			link.id = MANIFEST_ID;
			link.rel = "manifest";
			return link;
		}).href = MANIFEST_URL;

		ensureHeadTag('meta[name="theme-color"]', () => {
			const meta = document.createElement("meta");
			meta.name = "theme-color";
			return meta;
		}).content = THEME_COLOR;

		ensureHeadTag('meta[name="mobile-web-app-capable"]', () => {
			const meta = document.createElement("meta");
			meta.name = "mobile-web-app-capable";
			return meta;
		}).content = "yes";

		ensureHeadTag('meta[name="apple-mobile-web-app-capable"]', () => {
			const meta = document.createElement("meta");
			meta.name = "apple-mobile-web-app-capable";
			return meta;
		}).content = "yes";

		ensureHeadTag('meta[name="apple-mobile-web-app-title"]', () => {
			const meta = document.createElement("meta");
			meta.name = "apple-mobile-web-app-title";
			return meta;
		}).content = "StewardPro";

		ensureHeadTag('meta[name="apple-mobile-web-app-status-bar-style"]', () => {
			const meta = document.createElement("meta");
			meta.name = "apple-mobile-web-app-status-bar-style";
			return meta;
		}).content = "default";

		ensureHeadTag('link[rel="apple-touch-icon"][data-stewardpro="1"]', () => {
			const link = document.createElement("link");
			link.rel = "apple-touch-icon";
			link.dataset.stewardpro = "1";
			return link;
		}).href = APPLE_ICON;
	};

	const hideBanner = () => {
		if (banner) {
			banner.hidden = true;
		}
	};

	const dismissBanner = () => {
		localStorage.setItem(DISMISS_KEY, String(Date.now()));
		hideBanner();
	};

	const createBanner = () => {
		if (banner || document.getElementById(BANNER_ID)) {
			banner = document.getElementById(BANNER_ID);
			return banner;
		}

		banner = document.createElement("aside");
		banner.id = BANNER_ID;
		banner.className = "stewardpro-pwa-banner";
		banner.hidden = true;
		banner.innerHTML = `
			<img class="stewardpro-pwa-banner__icon" src="${ICON}" alt="StewardPro icon">
			<div class="stewardpro-pwa-banner__content">
				<p class="stewardpro-pwa-banner__title">Install StewardPro</p>
				<p class="stewardpro-pwa-banner__text" data-role="message"></p>
				<div class="stewardpro-pwa-banner__actions" data-role="actions"></div>
			</div>
			<button class="stewardpro-pwa-banner__close" type="button" aria-label="Dismiss install prompt">&times;</button>
		`;

		banner.querySelector(".stewardpro-pwa-banner__close").addEventListener("click", dismissBanner);
		document.body.appendChild(banner);
		return banner;
	};

	const setBannerContent = (message, actions) => {
		const root = createBanner();
		root.querySelector('[data-role="message"]').textContent = message;

		const actionsRoot = root.querySelector('[data-role="actions"]');
		actionsRoot.innerHTML = "";

		actions.forEach((action) => {
			const button = document.createElement("button");
			button.type = "button";
			button.className = `stewardpro-pwa-banner__button ${action.className}`;
			button.textContent = action.label;
			button.addEventListener("click", action.onClick);
			actionsRoot.appendChild(button);
		});

		root.hidden = !canShowBanner();
	};

	const promptInstall = async () => {
		if (!deferredPrompt) {
			return;
		}

		deferredPrompt.prompt();
		const choice = await deferredPrompt.userChoice;
		if (choice?.outcome !== "accepted") {
			dismissBanner();
			return;
		}

		localStorage.setItem(INSTALLED_KEY, "1");
		hideBanner();
		deferredPrompt = null;
	};

	const maybeShowIOSHelp = () => {
		if (!isIOS() || !isSafari() || isStandalone() || !canShowBanner()) {
			return;
		}

		setBannerContent(
			"Open Safari's share menu and choose Add to Home Screen to install StewardPro on this device.",
			[
				{ label: "Later", className: "stewardpro-pwa-banner__button--secondary", onClick: dismissBanner },
			]
		);
	};

	const registerInstallEvents = () => {
		window.addEventListener("beforeinstallprompt", (event) => {
			event.preventDefault();
			deferredPrompt = event;

			if (!canShowBanner()) {
				return;
			}

			setBannerContent(
				"Add StewardPro to your home screen for faster access to membership, finance, and Sabbath School workspaces.",
				[
					{ label: "Install", className: "stewardpro-pwa-banner__button--primary", onClick: promptInstall },
					{ label: "Later", className: "stewardpro-pwa-banner__button--secondary", onClick: dismissBanner },
				]
			);
		});

		window.addEventListener("appinstalled", () => {
			localStorage.setItem(INSTALLED_KEY, "1");
			hideBanner();
			deferredPrompt = null;
		});
	};

	const registerServiceWorker = async () => {
		if (!("serviceWorker" in navigator) || !isSecureOrigin()) {
			return;
		}

		try {
			await navigator.serviceWorker.register(SW_URL, { scope: "/" });
		} catch (error) {
			console.error("StewardPro PWA service worker registration failed.", error);
		}
	};

	const init = () => {
		if (!isRelevantRoute()) {
			return;
		}

		injectPwaMeta();
		registerInstallEvents();
		registerServiceWorker();
		maybeShowIOSHelp();
	};

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init, { once: true });
	} else {
		init();
	}
})();
