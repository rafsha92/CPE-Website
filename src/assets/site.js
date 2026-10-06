(function () {
  'use strict';
  var root = document.documentElement;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var mobile = window.matchMedia('(max-width: 600px)');
  var lang = root.lang === 'ms' ? 'ms' : 'en';
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.menu-toggle');
  var menu = document.querySelector('.mobile-nav');
  var form = document.querySelector('.contact-form');
  var floating = document.querySelector('.floating-contact');
  var process = document.querySelector('.process');
  var processButtons = process ? Array.from(process.querySelectorAll('.process-step')) : [];
  var processLine = document.querySelector('.process-progress');
  var processDetail = document.querySelector('.process-explanation');
  var activeProcess = -1;
  var manualProcess = false;
  var frame = false;
  var teamMedia = document.querySelector('.team-media');
  var observers = [];
  var contactObserver;
  var gsap = window.gsap;
  var ScrollTrigger = window.ScrollTrigger;
  var enhanced = Boolean(gsap && ScrollTrigger);
  var motionMedia;
  var revealed = new WeakSet();
  var heroPlayed = false;
  var refreshFrame = false;

  function setProcess(index) {
    if (index === activeProcess) return;
    activeProcess = index;
    processButtons.forEach(function (button, i) {
      button.classList.toggle('active', i <= index);
      button.setAttribute('aria-pressed', i === index ? 'true' : 'false');
    });
    if (processDetail && processButtons[index]) processDetail.textContent = processButtons[index].dataset.detail;
  }
  processButtons.forEach(function (button, index) {
    button.addEventListener('click', function () {
      manualProcess = true;
      setProcess(index);
      refreshMotion();
    });
  });
  function refreshMotion() {
    if (!enhanced || refreshFrame) return;
    refreshFrame = true;
    requestAnimationFrame(function () {
      refreshFrame = false;
      ScrollTrigger.refresh();
    });
  }
  function scrollUpdate() {
    frame = false;
    if (header) header.classList.toggle('scrolled', window.scrollY > 30);
    if (process && (!enhanced || reduced.matches)) {
      var rect = process.getBoundingClientRect();
      var progress = Math.max(0, Math.min(1, (window.innerHeight * .82 - rect.top) / (rect.height + window.innerHeight * .2)));
      if (processLine && !reduced.matches) processLine.style.transform = (mobile.matches ? 'scaleY(' : 'scaleX(') + progress + ')';
      if (!manualProcess && rect.bottom > 0 && rect.top < window.innerHeight) setProcess(Math.min(3, Math.floor(progress * 4)));
    }
    if (teamMedia && !enhanced) {
      var teamRect = teamMedia.parentElement.getBoundingClientRect();
      if (!reduced.matches && !mobile.matches && teamRect.top < window.innerHeight && teamRect.bottom > 0) {
        var amount = Math.max(-20, Math.min(20, (window.innerHeight / 2 - teamRect.top - teamRect.height / 2) * .035));
        teamMedia.style.transform = 'translateY(' + amount.toFixed(1) + 'px)';
      } else if (reduced.matches || mobile.matches) teamMedia.style.transform = '';
    }
  }
  function scheduleScroll() {
    manualProcess = false;
    if (!frame) { frame = true; requestAnimationFrame(scrollUpdate); }
  }
  window.addEventListener('scroll', scheduleScroll, { passive: true });
  window.addEventListener('resize', scheduleScroll, { passive: true });
  scrollUpdate();

  function settleDisclosures() {
    document.querySelectorAll('.faq-question').forEach(function (question) {
      var panel = document.getElementById(question.getAttribute('aria-controls'));
      if (!panel) return;
      if (panel._animation) {
        if (panel._animation.kill) panel._animation.kill();
        else panel._animation.cancel();
        panel._animation = null;
      }
      panel.style.removeProperty('height');
      panel.style.removeProperty('opacity');
      panel.hidden = question.getAttribute('aria-expanded') !== 'true';
    });
  }
  function setupNativeMotion() {
    root.dataset.motionEngine = 'native';
    root.dataset.motionState = reduced.matches ? 'reduced' : 'active';
    observers.forEach(function (observer) { observer.disconnect(); });
    observers = [];
    document.querySelectorAll('.motion-enter').forEach(function (el) { el.classList.remove('motion-enter'); });
    if (reduced.matches || !('IntersectionObserver' in window)) {
      settleDisclosures();
      return;
    }
    var revealObserver = new IntersectionObserver(function (entries, observer) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          revealed.add(entry.target);
          entry.target.classList.add('motion-enter');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: .15 });
    document.querySelectorAll('[data-reveal], .scope-comparison, .example').forEach(function (el) {
      if (!revealed.has(el)) revealObserver.observe(el);
    });
    observers.push(revealObserver);
  }

  function setupGSAPMotion() {
    gsap.registerPlugin(ScrollTrigger);
    // The same cubic-bezier curve as the CSS plan, with monotonic x inversion.
    gsap.registerEase('cpe-out', function (progress) {
      var low = 0, high = 1, time = progress;
      for (var i = 0; i < 12; i++) {
        time = (low + high) / 2;
        var inverse = 1 - time;
        var x = 3 * inverse * inverse * time * .16 + 3 * inverse * time * time * .3 + time * time * time;
        if (x < progress) low = time;
        else high = time;
      }
      return 1 - Math.pow(1 - time, 3);
    });
    root.dataset.motionEngine = 'gsap';
    motionMedia = gsap.matchMedia();
    motionMedia.add({
      desktop: '(min-width: 601px)',
      phone: '(max-width: 600px)',
      reduce: '(prefers-reduced-motion: reduce)'
    }, function (context) {
      var conditions = context.conditions;
      root.dataset.motionState = conditions.reduce ? 'reduced' : 'active';
      if (conditions.reduce) {
        settleDisclosures();
        return;
      }
      function once(target, play, identity) {
        if (!target || revealed.has(target)) return;
        ScrollTrigger.create({
          id: 'cpe-' + identity,
          trigger: target,
          start: function () { return 'top+=' + Math.round(target.offsetHeight * .15) + ' bottom'; },
          once: true,
          onEnter: function () {
            if (revealed.has(target)) return;
            revealed.add(target);
            target.dataset.motionPlayed = 'true';
            if (target.getBoundingClientRect().bottom <= 0) return;
            // Record callback-created tweens so media changes also restore them.
            context.add(play);
          }
        });
      }
      var hero = document.querySelector('.hero-media img');
      if (hero && !heroPlayed) {
        heroPlayed = true;
        gsap.fromTo(hero, { scale: 1.02 }, { scale: 1, duration: .7, ease: 'cpe-out', clearProps: 'transform' });
      }
      document.querySelectorAll('[data-reveal]').forEach(function (el, index) {
        once(el, function () {
          var type = el.dataset.reveal;
          var delay = parseFloat(getComputedStyle(el).getPropertyValue('--delay')) / 1000 || 0;
          var start = type === 'image' ? { clipPath: 'inset(0 100% 0 0)' } :
            type === 'fade' ? { opacity: .55 } : { y: 12, opacity: .55 };
          var end = type === 'image' ? { clipPath: 'inset(0 0 0 0)', duration: .5, clearProps: 'clipPath' } :
            { y: 0, opacity: 1, duration: type === 'fade' ? .25 : .35, clearProps: 'transform,opacity' };
          gsap.fromTo(el, start, Object.assign(end, { delay: delay, ease: 'cpe-out' }));
        }, 'reveal-' + index);
      });
      var scope = document.querySelector('.scope-comparison');
      once(scope, function () {
        gsap.fromTo(scope, { '--scope-progress': 0 }, { '--scope-progress': 1, duration: .45, ease: 'cpe-out' });
      }, 'scope');
      var example = document.querySelector('.example');
      once(example && example.querySelector('.bill-bars'), function () {
        example.dataset.motionPlayed = 'true';
        var timeline = gsap.timeline();
        timeline.fromTo(example.querySelectorAll('.bar-fill'), { scaleX: 0 }, {
          scaleX: 1, duration: .7, ease: 'cpe-out', clearProps: 'transform'
        }, 0);
        var equation = example.querySelector('.equation');
        timeline.to(equation, { backgroundColor: '#c9e9e4', duration: .3, ease: 'cpe-out' }, .65)
          .to(equation, { backgroundColor: '#e7f3f1', duration: .3, ease: 'cpe-out', clearProps: 'backgroundColor' }, .95);
      }, 'bill-comparison');
      if (process && processLine) {
        var start = { scaleX: 1, scaleY: 1 };
        var end = { scaleX: 1, scaleY: 1, duration: 1, ease: 'none' };
        start[conditions.phone ? 'scaleY' : 'scaleX'] = 0;
        end.scrollTrigger = {
          id: 'cpe-process',
          trigger: process,
          start: 'top 82%',
          end: 'bottom 62%',
          scrub: true,
          invalidateOnRefresh: true,
          onUpdate: function (trigger) {
            if (!manualProcess && trigger.isActive) setProcess(Math.min(3, Math.floor(trigger.progress * 4)));
          }
        };
        gsap.fromTo(processLine, start, end);
      }
      if (teamMedia && conditions.desktop) {
        gsap.fromTo(teamMedia, { y: -20 }, {
          y: 20, ease: 'none',
          scrollTrigger: {
            id: 'cpe-team-parallax',
            trigger: teamMedia.parentElement,
            start: 'top bottom',
            end: 'bottom top',
            scrub: .25,
            invalidateOnRefresh: true
          }
        });
      }
    });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(refreshMotion);
    window.addEventListener('load', refreshMotion, { once: true });
  }

  if (enhanced) {
    try { setupGSAPMotion(); }
    catch (error) {
      if (motionMedia) motionMedia.revert();
      enhanced = false;
      setupNativeMotion();
    }
  } else setupNativeMotion();
  if (reduced.addEventListener) reduced.addEventListener('change', function () {
    if (!enhanced) setupNativeMotion();
    if (reduced.matches) settleDisclosures();
    scrollUpdate();
  });

  if (floating && 'IntersectionObserver' in window) {
    var contact = document.querySelector('#contact');
    if (contact) {
      contactObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          floating.classList.toggle('hidden', entry.isIntersecting);
          if (entry.isIntersecting) floating.setAttribute('tabindex', '-1');
          else floating.removeAttribute('tabindex');
        });
      }, { threshold: .1 });
      contactObserver.observe(contact);
    }
  }
  function closeMenu(returnFocus) {
    if (!toggle || !menu) return;
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', lang === 'ms' ? 'Buka menu' : 'Open menu');
    menu.classList.remove('open');
    menu.hidden = true;
    document.body.classList.remove('menu-open');
    header.classList.remove('menu-active');
    if (returnFocus) toggle.focus();
  }
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      if (toggle.getAttribute('aria-expanded') === 'true') { closeMenu(true); return; }
      toggle.setAttribute('aria-expanded', 'true');
      toggle.setAttribute('aria-label', lang === 'ms' ? 'Tutup menu' : 'Close menu');
      menu.hidden = false;
      menu.classList.add('open');
      header.classList.add('menu-active');
      document.body.classList.add('menu-open');
      menu.querySelector('a').focus();
    });
    menu.querySelectorAll('a').forEach(function (link) { link.addEventListener('click', function () { closeMenu(false); }); });
    document.addEventListener('keydown', function (event) {
      if (toggle.getAttribute('aria-expanded') !== 'true') return;
      if (event.key === 'Escape') { event.preventDefault(); closeMenu(true); }
      if (event.key === 'Tab') {
        var items = [toggle].concat(Array.from(menu.querySelectorAll('a')));
        var first = items[0], last = items[items.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    });
    window.addEventListener('resize', function () { if (window.innerWidth > 900) closeMenu(false); }, { passive: true });
  }
  var tabs = Array.from(document.querySelectorAll('[role=tab]'));
  function selectTab(button) {
    tabs.forEach(function (tab) {
      var selected = tab === button;
      tab.setAttribute('aria-selected', selected ? 'true' : 'false');
      tab.tabIndex = selected ? 0 : -1;
      var panel = document.getElementById(tab.getAttribute('aria-controls'));
      if (panel) panel.hidden = !selected;
    });
  }
  tabs.forEach(function (button, index) {
    button.addEventListener('click', function () { selectTab(button); });
    button.addEventListener('keydown', function (event) {
      var target = -1;
      if (event.key === 'ArrowRight') target = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') target = (index - 1 + tabs.length) % tabs.length;
      if (event.key === 'Home') target = 0;
      if (event.key === 'End') target = tabs.length - 1;
      if (target >= 0) { event.preventDefault(); selectTab(tabs[target]); tabs[target].focus(); }
    });
  });
  var premises = Array.from(document.querySelectorAll('.premise-option'));
  premises.forEach(function (button) {
    button.addEventListener('click', function () {
      premises.forEach(function (option) { option.setAttribute('aria-pressed', option === button ? 'true' : 'false'); });
      var result = document.querySelector('.premise-result');
      if (result) result.textContent = button.dataset.note;
      var select = document.querySelector('[name=premises]');
      if (select && Array.from(select.options).some(function (option) { return option.value === button.dataset.value; })) select.value = button.dataset.value;
    });
  });
  var measurements = Array.from(document.querySelectorAll('.measurement-step'));
  measurements.forEach(function (button) {
    button.addEventListener('click', function () {
      var wasOpen = button.getAttribute('aria-expanded') === 'true';
      measurements.forEach(function (other) {
        var open = other === button && !wasOpen;
        other.setAttribute('aria-expanded', open ? 'true' : 'false');
        var description = document.getElementById(other.getAttribute('aria-controls'));
        if (description) description.hidden = !open;
      });
      refreshMotion();
    });
  });
  function animatePanel(panel, open) {
    var current = panel.hidden ? 0 : panel.getBoundingClientRect().height;
    if (panel._animation) {
      if (panel._animation.kill) panel._animation.kill();
      else panel._animation.cancel();
      panel._animation = null;
    }
    if (reduced.matches || (!enhanced && !panel.animate)) {
      panel.style.removeProperty('height');
      panel.style.removeProperty('opacity');
      panel.hidden = !open;
      refreshMotion();
      return;
    }
    panel.hidden = false;
    panel.style.removeProperty('height');
    var full = panel.scrollHeight;
    if (enhanced) {
      panel._animation = gsap.fromTo(panel,
        { height: current, opacity: open ? .55 : 1 },
        { height: open ? full : 0, opacity: open ? 1 : .55, duration: .22, ease: 'cpe-out', overwrite: true,
          onComplete: function () {
            panel.hidden = !open;
            gsap.set(panel, { clearProps: 'height,opacity' });
            panel._animation = null;
            refreshMotion();
          }
        });
      return;
    }
    var animation = panel.animate([{ height: current + 'px', opacity: open ? .5 : 1 }, { height: (open ? full : 0) + 'px', opacity: open ? 1 : .5 }], { duration: 220, easing: 'cubic-bezier(.16,1,.3,1)' });
    panel._animation = animation;
    animation.onfinish = function () { panel.hidden = !open; panel._animation = null; refreshMotion(); };
  }
  var questions = Array.from(document.querySelectorAll('.faq-question'));
  questions.forEach(function (button) {
    button.addEventListener('click', function () {
      var selectedOpen = button.getAttribute('aria-expanded') !== 'true';
      questions.forEach(function (other) {
        var open = other === button && selectedOpen;
        var wasOpen = other.getAttribute('aria-expanded') === 'true';
        other.setAttribute('aria-expanded', open ? 'true' : 'false');
        other.closest('.faq-item').classList.toggle('open', open);
        var use = other.querySelector('use');
        if (use) use.setAttribute('href', open ? '#i-minus' : '#i-plus');
        var panel = document.getElementById(other.getAttribute('aria-controls'));
        if (panel && open !== wasOpen) animatePanel(panel, open);
      });
    });
  });
  if (form) {
    form.querySelector('[type=submit]').disabled = false;
    var status = form.querySelector('.form-status');
    function error(field, message) {
      field.setAttribute('aria-invalid', message ? 'true' : 'false');
      var el = document.getElementById(field.id + '-error');
      if (el) el.textContent = message;
    }
    form.querySelectorAll('input,select,textarea').forEach(function (field) {
      field.addEventListener('input', function () {
        if (field.getAttribute('aria-invalid') === 'true') error(field, '');
      });
    });
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var fields = ['name', 'phone', 'location', 'premises'];
      var invalid = null;
      fields.forEach(function (name) {
        var field = form.elements[name], message = '';
        if (!field.value.trim()) message = lang === 'ms' ? 'Sila lengkapkan maklumat ini.' : 'Please complete this field.';
        if (name === 'phone' && field.value.trim() && !/^\+?[\d\s()-]{8,25}$/.test(field.value.trim())) message = lang === 'ms' ? 'Masukkan nombor telefon yang sah.' : 'Enter a valid telephone number.';
        var digits = field.value.replace(/\D/g, '');
        if (name === 'phone' && field.value.trim() && (digits.length < 8 || digits.length > 15)) message = lang === 'ms' ? 'Masukkan 8 hingga 15 digit.' : 'Enter 8 to 15 digits.';
        error(field, message);
        if (message && !invalid) invalid = field;
      });
      if (invalid) {
        status.classList.add('error');
        status.textContent = lang === 'ms' ? 'Semak medan yang ditandakan sebelum menyediakan mesej.' : 'Check the marked fields before preparing your message.';
        invalid.focus();
        return;
      }
      var button = form.querySelector('[type=submit]');
      var label = button.querySelector('span');
      var original = label.textContent;
      button.disabled = true;
      label.textContent = lang === 'ms' ? 'Menyediakan mesej…' : 'Preparing message…';
      var values = new FormData(form);
      var text = lang === 'ms' ? 'Salam Pasukan CPE. Saya ingin semak kesesuaian premis saya.' : 'Hello CPE team. I would like to check the suitability of my premises.';
      text += '\n\n' + (lang === 'ms' ? 'Nama: ' : 'Name: ') + values.get('name');
      text += '\n' + (lang === 'ms' ? 'Telefon: ' : 'Telephone: ') + values.get('phone');
      text += '\n' + (lang === 'ms' ? 'Lokasi: ' : 'Location: ') + values.get('location');
      var selected = form.elements.premises.selectedOptions[0].textContent;
      text += '\n' + (lang === 'ms' ? 'Jenis premis: ' : 'Premises type: ') + selected;
      if (values.get('equipment')) text += '\n' + (lang === 'ms' ? 'Peralatan / nota: ' : 'Equipment / notes: ') + values.get('equipment');
      var url = 'https://wa.me/' + form.dataset.phone + '?text=' + encodeURIComponent(text);
      status.classList.remove('error');
      status.replaceChildren();
      status.append(document.createTextNode(lang === 'ms' ? 'Mesej tersedia. Semak dan hantar melalui WhatsApp. ' : 'Your message is ready. Review and send it in WhatsApp. '));
      var link = document.createElement('a');
      link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer';
      link.textContent = lang === 'ms' ? 'Buka mesej WhatsApp' : 'Open WhatsApp message';
      status.append(link);
      window.open(url, '_blank', 'noopener,noreferrer');
      button.disabled = false;
      label.textContent = original;
    });
  }
  window.addEventListener('pagehide', function (event) {
    if (event.persisted) return;
    if (motionMedia) motionMedia.revert();
    if (contactObserver) contactObserver.disconnect();
    settleDisclosures();
    observers.forEach(function (observer) { observer.disconnect(); });
  });
}());
