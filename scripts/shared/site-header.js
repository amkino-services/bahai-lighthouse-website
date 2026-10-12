document.addEventListener('DOMContentLoaded', () => {
  const target = document.getElementById('global-header');
  if (!target) return;

  target.innerHTML = `
    <header class="site-header lighthouse-header global-header">

      <a
        class="brand lighthouse-brand"
        href="/"
        aria-label="العودة إلى الصفحة الرئيسية"
      >
        <img
          src="/assets/brand/lighthouse-mark.svg"
          alt=""
          class="lighthouse-header-logo"
        >

        <span>
          <strong>المنارة البهائية</strong>
          <small>مساحة رقمية بهائية لخدمة المجتمع</small>
        </span>
      </a>

      <button
        class="mobile-menu-toggle"
        type="button"
        aria-expanded="false"
        aria-controls="global-navigation"
        aria-label="فتح القائمة"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <nav
        id="global-navigation"
        class="main-nav global-nav"
        aria-label="التنقل الرئيسي"
      >

        <a href="/">الرئيسية</a>

        <a href="/#purpose">هدف المنارة البهائية</a>

        <div class="nav-dropdown">

          <button
            class="nav-dropdown-toggle"
            type="button"
            aria-expanded="false"
            aria-haspopup="true"
          >
            <span>الأقسام</span>
          </button>

          <div class="nav-dropdown-menu">

            <a href="/prayers">
              <span>الأدعية والمناجاة</span>
              <small class="available-label">متاح</small>
            </a>

            <span class="nav-disabled">
              <span>المكتبة البهائية</span>
              <small>قريباً</small>
            </span>

            <span class="nav-disabled">
              <span>المكتبة الصوتية</span>
              <small>قريباً</small>
            </span>

            <a href="/calendar">
              <span>المناسبات والأيام المباركة</span>
              <small class="available-label">متاح</small>
            </a>

            <a href="/community">
              <span>موارد للمجتمعات</span>
              <small class="available-label">متاح</small>
            </a>

            <a href="/tools">
              <span>تطبيقات المنارة</span>
              <small>متاح</small>
            </a>

          </div>
        </div>

        <a href="/#community">للزوار</a>

        <a href="/#about">حول المشروع</a>

      </nav>

    </header>
  `;

  const mobileToggle = target.querySelector('.mobile-menu-toggle');
  const nav = target.querySelector('.global-nav');
  const dropdown = target.querySelector('.nav-dropdown');
  const dropdownToggle = target.querySelector('.nav-dropdown-toggle');

  mobileToggle.addEventListener('click', () => {
    const open = mobileToggle.getAttribute('aria-expanded') === 'true';

    mobileToggle.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('is-open', !open);
  });

  dropdownToggle.addEventListener('click', (event) => {
    event.stopPropagation();

    const open = dropdownToggle.getAttribute('aria-expanded') === 'true';

    dropdownToggle.setAttribute('aria-expanded', String(!open));
    dropdown.classList.toggle('is-open', !open);
  });

  document.addEventListener('click', (event) => {
    if (!dropdown.contains(event.target)) {
      dropdown.classList.remove('is-open');
      dropdownToggle.setAttribute('aria-expanded', 'false');
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      dropdown.classList.remove('is-open');
      dropdownToggle.setAttribute('aria-expanded', 'false');

      nav.classList.remove('is-open');
      mobileToggle.setAttribute('aria-expanded', 'false');
    }
  });

  // Highlight the current page in the shared navigation
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';

  if (currentPage === 'index.html') {
    // Homepage section-aware navigation
    const homeLink = target.querySelector(
      '.global-nav > a[href="/"]'
    );

    const purposeLink = target.querySelector(
      '.global-nav > a[href="/#purpose"]'
    );

    const communityLink = target.querySelector(
      '.global-nav > a[href="/#community"]'
    );

    const aboutLink = target.querySelector(
      '.global-nav > a[href="/#about"]'
    );

    const sections = [
      {
        id: 'top',
        element: document.getElementById('top'),
        control: homeLink,
      },
      {
        id: 'purpose',
        element: document.getElementById('purpose'),
        control: purposeLink,
      },
      {
        id: 'sections',
        element: document.getElementById('sections'),
        control: dropdownToggle,
      },
      {
        id: 'community',
        element: document.getElementById('community'),
        control: communityLink,
      },
      {
        id: 'about',
        element: document.getElementById('about'),
        control: aboutLink,
      },
    ].filter((item) => item.element && item.control);

    const controls = [
      homeLink,
      purposeLink,
      dropdownToggle,
      communityLink,
      aboutLink,
    ].filter(Boolean);

    const setCurrentSection = (activeControl) => {
      controls.forEach((control) => {
        control.classList.toggle(
          'nav-current',
          control === activeControl
        );
      });
    };

    const updateCurrentSection = () => {
      const headerHeight =
        target.querySelector('.site-header')
          ?.getBoundingClientRect().height || 0;

      const probe = window.scrollY + headerHeight + 120;

      let active = sections[0];

      sections.forEach((item) => {
        const top =
          window.scrollY +
          item.element.getBoundingClientRect().top;

        if (top <= probe) {
          active = item;
        }
      });

      if (active) {
        setCurrentSection(active.control);
      }
    };

    updateCurrentSection();

    let ticking = false;

    window.addEventListener(
      'scroll',
      () => {
        if (ticking) return;

        ticking = true;

        window.requestAnimationFrame(() => {
          updateCurrentSection();
          ticking = false;
        });
      },
      { passive: true }
    );

    window.addEventListener('resize', updateCurrentSection);
  }

  if (currentPage === 'prayers.html') {
    const prayersLink = target.querySelector(
      '.nav-dropdown-menu a[href="/prayers"]'
    );

    if (prayersLink) {
      prayersLink.classList.add('nav-current');
      dropdownToggle.classList.add('nav-current');
    }
  }

});
