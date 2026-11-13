// ////////////////////////////////////////////////////////////////////////////////////// //
// Check if pause server is running and show or hide button accordingly                    //
// ////////////////////////////////////////////////////////////////////////////////////// //

fetch('http://127.0.0.1:6969/status')
  .then(response => {
    if (response.ok) {
      document.getElementById('pauseBtn').style.display = 'inline';
    } else {
      document.getElementById('pauseBtn').style.display = 'none';
    }
  })
  .catch(() => {
    const btn = document.getElementById('pauseBtn');
    if (btn) btn.style.display = 'none';
  });

// ////////////////////////////////////////////////////////////////////////////////////// //
// Banner and Clock Logic                                                                 //
// ////////////////////////////////////////////////////////////////////////////////////// //

function resizeBannerText() {
  const container = document.querySelector('.banner-container');
  const title = document.querySelector('.banner-title');
  const date = document.querySelector('.banner-date');
  const counters = document.querySelector('.challenge-counters');
  const clock = document.getElementById('rdo-clock');

  if (!container) return;

  const containerWidth = container.offsetWidth;
  const minWidth = 400;
  const maxWidth = 850;
  const scale = Math.max(minWidth, Math.min(containerWidth, maxWidth)) / maxWidth;

  if (title) title.style.fontSize = (2.5 * scale) + 'rem';
  if (date) date.style.fontSize = (1.4 * scale) + 'rem';
  if (counters) counters.style.fontSize = (1.25 * scale) + 'rem';
  if (clock) clock.style.fontSize = (2 * scale) + 'rem';
}

window.addEventListener('resize', resizeBannerText);
window.addEventListener('load', resizeBannerText);

const offsetSeconds = -600; // -10 minutes offset for game clock

function getInGameHour() {
  const now = new Date();
  const utcSeconds = now.getUTCHours() * 3600 + now.getUTCMinutes() * 60 + now.getUTCSeconds();
  const gameSeconds = (utcSeconds * 30 + offsetSeconds) % 86400;
  return Math.floor(gameSeconds / 3600) + Math.floor((gameSeconds % 3600) / 60) / 60;
}

function updateAllTimeFunctions() {
  const hourFloat = getInGameHour();
  const gameHours = Math.floor(hourFloat).toString().padStart(2, '0');
  const gameMinutes = Math.floor((hourFloat % 1) * 60).toString().padStart(2, '0');
  const clockEl = document.getElementById("rdo-clock");
  if (clockEl) clockEl.textContent = `${gameHours}:${gameMinutes}`;

  const banner = document.querySelector('.banner-image');
  const clock = document.querySelector('.rdo-clock');

  if (banner && clock) {
    if (hourFloat >= 22 || hourFloat < 5) {
      if (!banner.src.endsWith("RDO_Banner_Wide_Night.jpg")) banner.src = "HTML/images/RDO_Banner_Wide_Night.jpg";
      clock.classList.add('night-glow');
    } else {
      if (!banner.src.endsWith("RDO_Banner_Wide.jpg")) banner.src = "HTML/images/RDO_Banner_Wide.jpg";
      clock.classList.remove('night-glow');
    }
  }
}

setInterval(updateAllTimeFunctions, 1000);
updateAllTimeFunctions();

// ////////////////////////////////////////////////////////////////////////////////////// //
// Cycle Descriptions                                                                     //
// ////////////////////////////////////////////////////////////////////////////////////// //

function cycleDesc(event, btn) {
  event.preventDefault();
  event.stopPropagation();

  try {
    const descs = JSON.parse(btn.getAttribute('data-descs'));
    let currentIdx = parseInt(btn.getAttribute('data-idx'), 10);
    currentIdx = (currentIdx + 1) % descs.length;
    btn.setAttribute('data-idx', currentIdx);

    const targetId = btn.getAttribute('data-target');
    const targetDiv = document.getElementById(targetId);
    if (targetDiv) {
      targetDiv.textContent = descs[currentIdx];
    }

    let rotation = parseInt(btn.getAttribute('data-rotation') || '0', 10);
    rotation += 180;
    btn.style.transform = `rotate(${rotation}deg)`;
    btn.setAttribute('data-rotation', rotation);
  } catch (e) {
    console.error("Error cycling description:", e);
  }
}
window.cycleDesc = cycleDesc;

// ////////////////////////////////////////////////////////////////////////////////////// //
// Toggle Nazar Map Zoom                                                                  //
// ////////////////////////////////////////////////////////////////////////////////////// //

function toggleNazarZoom(img) {
  if (img.dataset.hasZoom !== "true") return;

  const currentSrc = img.src.split('/').pop();
  const stdSrc = img.dataset.standard.split('/').pop();
  const zoomSrc = img.dataset.zoom ? img.dataset.zoom.split('/').pop() : "";
  const photoSrc = img.dataset.photo ? img.dataset.photo.split('/').pop() : "";

  if (currentSrc === stdSrc) {
    if (zoomSrc) {
      img.src = img.dataset.zoom;
    } else if (photoSrc) {
      img.src = img.dataset.photo;
    }
  } else if (currentSrc === zoomSrc) {
    if (photoSrc) {
      img.src = img.dataset.photo;
    } else {
      img.src = img.dataset.standard;
    }
  } else {
    img.src = img.dataset.standard;
  }
}
window.toggleNazarZoom = toggleNazarZoom;

// Nazar Map 5-Second Dissolve
setTimeout(() => {
  const img = document.getElementById('nazar-map-img');
  if (!img) return;

  const currentFilename = img.src.split('/').pop();
  const targetSrc = img.dataset.finalTarget;
  if (!targetSrc) return;
  const targetFilename = targetSrc.split('/').pop();

  if (currentFilename === targetFilename) return;

  img.style.opacity = 0;
  setTimeout(() => {
    img.src = targetSrc;
    img.dataset.standard = targetSrc;
    img.style.opacity = 1;
  }, 800);
}, 5000);

// ////////////////////////////////////////////////////////////////////////////////////// //
// Main Tracker & Gold Logic                                                              //
// ////////////////////////////////////////////////////////////////////////////////////// //

document.addEventListener("DOMContentLoaded", function() {
  const config = window.RDO_CONFIG || {};
  const PYTHON_STREAK_OVERRIDE = config.streakOverride !== undefined ? config.streakOverride : -1;
  const PYTHON_CHALLENGE_TIMESTAMP = config.challengeTimestamp || Math.floor(Date.now() / 1000);
  const PYTHON_ENABLE_DEBUG = !!config.enableDebug;
  const RAW_EVENTS_DATA = config.rawEventsData || [];

  const LS_STREAK_COUNT = 'rdoStreakCount';
  const LS_LAST_COMPLETION_DATE = 'rdoLastCompletionDate';
  const LS_CHALLENGE_STATUS = 'rdoChallengeStatus';
  const LS_STREAK_FOR_MULTIPLIER = 'rdoStreakForMultiplier';
  const MAX_RDO_STREAK = 28;
  const LS_GOLD_LOG = 'rdoGoldLog';
  const LS_LAST_KNOWN_TIMESTAMP = 'rdoLastKnownTimestamp';
  const LS_CHART_VIEW_MODE = 'rdoChartViewMode';

  let activeChartView = localStorage.getItem(LS_CHART_VIEW_MODE) || 'gold';

  const allCheckboxes = document.querySelectorAll('.challenge-checkbox');
  const generalCheckboxes = document.querySelectorAll('.challenge-checkbox[id^="challenge_"]');
  const roleCheckboxes = document.querySelectorAll('.challenge-checkbox[id^="role-challenge_"]');

  function getRDODayKey() {
    const now = new Date();
    const resetTimeHours = 6;
    const date = new Date(now.getTime());
    if (date.getUTCHours() < resetTimeHours) {
      date.setUTCDate(date.getUTCDate() - 1);
    }
    return date.toISOString().split('T')[0];
  }

  function getChallengeDateKey() {
    const date = new Date(PYTHON_CHALLENGE_TIMESTAMP * 1000);
    return date.toISOString().split('T')[0];
  }

  function getDateDifferenceInDays(dateStr1, dateStr2) {
    const date1 = new Date(`${dateStr1}T12:00:00Z`);
    const date2 = new Date(`${dateStr2}T12:00:00Z`);
    return Math.round(Math.abs(date2 - date1) / (1000 * 60 * 60 * 24));
  }

  function setStreakCount(newCount, setCompleted) {
    const count = Math.min(Math.max(0, newCount), MAX_RDO_STREAK);
    localStorage.setItem(LS_STREAK_COUNT, count);
    if (setCompleted) {
      localStorage.setItem(LS_LAST_COMPLETION_DATE, getRDODayKey());
      localStorage.setItem(LS_CHALLENGE_STATUS, 'completed');
    } else {
      localStorage.removeItem(LS_LAST_COMPLETION_DATE);
      localStorage.removeItem(LS_CHALLENGE_STATUS);
    }
  }

  function getMultiplier() {
    const currentStreak = parseInt(localStorage.getItem(LS_STREAK_COUNT) || '0', 10);
    if (currentStreak >= 22) return 2.5;
    if (currentStreak >= 15) return 2.0;
    if (currentStreak >= 8) return 1.5;
    return 1.0;
  }

  function formatGoldForDisplay(goldValue) {
    const fixedValue = goldValue.toFixed(2);
    const parts = fixedValue.split('.');
    return `<span>${parts[0]}</span><span class="gold-decimal">.${parts[1]}</span> Gold Bars`;
  }

  function debugGoldStats(daily, week, running, goldLog) {
    if (!PYTHON_ENABLE_DEBUG) return;
    console.group(`%cRDO GOLD STATS`, 'color: #000; background: #FFC107; padding: 4px; border-radius: 4px; font-weight: bold;');
    console.table({
      "Current Streak (Live)": localStorage.getItem(LS_STREAK_COUNT) + " Days",
      "Multiplier Lock (Base)": localStorage.getItem(LS_STREAK_FOR_MULTIPLIER) + " Days",
      "Multiplier Value": getMultiplier() + "x",
      "Daily Total": daily.toFixed(2),
      "Streak Week Total": week.toFixed(2),
      "Streak Running Total": running.toFixed(2)
    });
    console.groupCollapsed("Full Gold Log History");
    console.table(goldLog);
    console.groupEnd();
    console.groupEnd();
  }

  function calculateDailyGoldTotal(completedGeneral, completedRole) {
    const BASE_REWARD = 0.10;
    const COMPLETION_BONUS_BASE = 0.30;
    const multiplier = getMultiplier();
    const completionBonusAmount = COMPLETION_BONUS_BASE * multiplier;
    const generalGold = (completedGeneral * BASE_REWARD) * multiplier;
    const generalBonus = (completedGeneral === 7) ? completionBonusAmount : 0;
    const roleGold = (completedRole * BASE_REWARD) * multiplier;
    const roleBonus = (completedRole === 9) ? completionBonusAmount : 0;

    const gpcEl = document.getElementById('gold-per-challenge');
    const cbrEl = document.getElementById('completion-bonus-reward');
    if (gpcEl) gpcEl.innerHTML = formatGoldForDisplay(BASE_REWARD * multiplier);
    if (cbrEl) cbrEl.innerHTML = formatGoldForDisplay(completionBonusAmount);

    return Math.round((generalGold + generalBonus + roleGold + roleBonus) * 100) / 100;
  }

  function logDailyGold(goldAmount, streakCount, generalCount, roleCount) {
    const today = getRDODayKey();
    if (getChallengeDateKey() !== today) return;

    let goldLog = JSON.parse(localStorage.getItem(LS_GOLD_LOG)) || [];
    const todayEntryIndex = goldLog.findIndex(entry => entry.date === today);
    const newEntry = { date: today, gold: goldAmount, streak: streakCount, general: generalCount, role: roleCount };

    if (todayEntryIndex > -1) {
      goldLog[todayEntryIndex] = newEntry;
    } else {
      goldLog.push(newEntry);
    }
    while (goldLog.length > 28) goldLog.shift();
    localStorage.setItem(LS_GOLD_LOG, JSON.stringify(goldLog));
  }

  // Upcoming Events Ticker Logic
  const LS_EVENT_OFFSET = 'rdoEventOffset';
  let currentEventOffset = parseInt(localStorage.getItem(LS_EVENT_OFFSET) || '0', 10);

  function updateOffsetDisplay() {
    const display = document.getElementById('event-offset-display');
    if (!display) return;
    if (currentEventOffset > 0) {
      display.textContent = '+' + currentEventOffset + 's';
      display.style.color = '#88ff88';
    } else if (currentEventOffset < 0) {
      display.textContent = currentEventOffset + 's';
      display.style.color = '#ff8888';
    } else {
      display.textContent = '0s';
      display.style.color = '#999';
    }
  }

  function updateUpcomingEvents() {
    const container = document.getElementById('upcoming-events-list');
    if (!container || !RAW_EVENTS_DATA.length) return;

    const now = new Date();
    const JOIN_WINDOW_MS = 3 * 60 * 1000;
    const offsetMs = currentEventOffset * 1000;

    let candidates = [];
    function getEventDate(timeStr, dayOffset) {
      const [h, m] = timeStr.split(':').map(Number);
      const d = new Date();
      d.setUTCHours(h, m, 0, 0);
      if (dayOffset > 0) {
        d.setUTCDate(d.getUTCDate() + dayOffset);
      }
      return d;
    }

    RAW_EVENTS_DATA.forEach(evt => {
      candidates.push({ ...evt, dt: getEventDate(evt.time, 0) });
      candidates.push({ ...evt, dt: getEventDate(evt.time, 1) });
    });

    const activeEvents = candidates.filter(e => {
      return (e.dt.getTime() + offsetMs + JOIN_WINDOW_MS) > now.getTime();
    });

    activeEvents.sort((a, b) => a.dt - b.dt);
    const next5 = activeEvents.slice(0, 5);

    let html = '<ul style="list-style: none; padding: 0; margin: 0;">';
    next5.forEach(e => {
      const diffMs = (e.dt.getTime() + offsetMs) - now.getTime();
      let timeDisplay = "";
      let rowBgColor = "transparent";
      let rowPadding = "1px 0";
      let textColor = "#ccc";
      let timeColor = "#bbb";
      let textClass = "";

      const localH = e.dt.getHours().toString().padStart(2, '0');
      const localM = e.dt.getMinutes().toString().padStart(2, '0');
      let eventTimeStr = `${localH}:${localM}`;
      let maxNameLength = 27;

      if (diffMs > 0) {
        const diffMins = Math.floor(diffMs / 60000);
        if (diffMins < 60) {
          timeDisplay = `${diffMins}m`;
        } else {
          timeDisplay = `${Math.floor(diffMins / 60)}h ${diffMins % 60}m`;
        }
      } else {
        textClass = "active-event-glow";
        const msPast = Math.abs(diffMs);
        rowPadding = "2px 4px";
        textColor = "#fff";
        timeColor = "#ddd";

        const msRemaining = JOIN_WINDOW_MS - msPast;
        const secsRemaining = Math.max(0, Math.floor(msRemaining / 1000));
        eventTimeStr = `${Math.floor(secsRemaining / 60)}:${(secsRemaining % 60).toString().padStart(2, '0')}`;

        if (msPast < 60000) {
          rowBgColor = "#333333";
          timeDisplay = "Now";
        } else if (msPast < 120000) {
          rowBgColor = "#555500";
          timeDisplay = "Now";
        } else {
          rowBgColor = "#550000";
          timeDisplay = "<1min";
        }
      }

      let nameDisplay = e.name;
      if (nameDisplay.length > maxNameLength) {
        nameDisplay = nameDisplay.substring(0, maxNameLength - 2) + "..";
      }

      html += `
        <li style="display: flex; justify-content: space-between; align-items: center; padding: ${rowPadding}; border-bottom: 1px solid #1a1a1a; font-size: 0.85rem; color: ${textColor}; background-color: ${rowBgColor}; border-radius: 2px; margin-bottom: 1px; transition: background-color 0.5s;">
            <div style="line-height: 1;">
                <span class="${textClass}" style="font-family: 'hapna', sans-serif; letter-spacing: -0.05em;">${nameDisplay}</span>
                <span style="font-size: 0.7rem; color: ${timeColor}; margin-left: 4px; letter-spacing: -0.05em;">(${timeDisplay})</span>
            </div>
            <span class="${textClass}" style="color: #FFC107; font-family: 'RDOFont', sans-serif; font-size: 1.0rem; letter-spacing: 1px; line-height: 1;">${eventTimeStr}</span>
        </li>
      `;
    });
    html += '</ul>';
    container.innerHTML = html;
  }

  setInterval(updateUpcomingEvents, 1000);
  window.addEventListener('load', updateUpcomingEvents);

  const offsetUp = document.getElementById('event-offset-up');
  const offsetDown = document.getElementById('event-offset-down');
  if (offsetUp) {
    offsetUp.addEventListener('click', () => {
      currentEventOffset += 1;
      localStorage.setItem(LS_EVENT_OFFSET, currentEventOffset);
      updateOffsetDisplay();
      updateUpcomingEvents();
    });
  }
  if (offsetDown) {
    offsetDown.addEventListener('click', () => {
      currentEventOffset -= 1;
      localStorage.setItem(LS_EVENT_OFFSET, currentEventOffset);
      updateOffsetDisplay();
      updateUpcomingEvents();
    });
  }
  updateOffsetDisplay();

  function calculateLogSums(currentStreak) {
    if (currentStreak === 0) return { week: 0, running: 0 };
    const goldLog = JSON.parse(localStorage.getItem(LS_GOLD_LOG)) || [];

    let minWeekStreak = 1;
    if (currentStreak >= 22) minWeekStreak = 22;
    else if (currentStreak >= 15) minWeekStreak = 15;
    else if (currentStreak >= 8) minWeekStreak = 8;

    let weekTotal = 0.0;
    let runningTotal = 0.0;
    let lastStreakVal = -1;

    for (let i = goldLog.length - 1; i >= 0; i--) {
      const entry = goldLog[i];
      const val = parseFloat(entry.gold || 0);
      const s = parseInt(entry.streak || 0);

      if (s === 0) break;
      if (lastStreakVal !== -1 && s > lastStreakVal) break;

      runningTotal += val;
      if (s >= minWeekStreak) {
        weekTotal += val;
      }
      lastStreakVal = s;
    }
    return { week: weekTotal, running: runningTotal };
  }

  function renderGoldLogChart() {
    const GOLD_CHART_MULTIPLIER = 12;
    const container = document.getElementById('gold-log-chart-container');
    const infoDisplay = document.getElementById('chart-info-display');
    if (!container || !infoDisplay) return;

    if (!window.rdoAudioCtx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        window.rdoAudioCtx = new AudioCtx();
        const unlockAudio = () => {
          if (window.rdoAudioCtx.state === 'suspended') window.rdoAudioCtx.resume();
          document.removeEventListener('click', unlockAudio);
        };
        document.addEventListener('click', unlockAudio);
      }
    }

    function playHoverTick() {
      const ctx = window.rdoAudioCtx;
      if (!ctx || ctx.state === 'suspended') return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(1200, ctx.currentTime);
      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
      osc.start();
      osc.stop(ctx.currentTime + 0.05);
    }

    infoDisplay.innerHTML = '&nbsp;';
    const goldLog = JSON.parse(localStorage.getItem(LS_GOLD_LOG)) || [];
    container.innerHTML = '';

    const dateList = [];
    const baseDate = new Date(getRDODayKey() + 'T12:00:00Z');
    for (let i = 27; i >= 0; i--) {
      const d = new Date(baseDate.getTime() - i * 24 * 60 * 60 * 1000);
      dateList.push(d.toISOString().split('T')[0]);
    }

    const entryMap = {};
    goldLog.forEach(entry => { entryMap[entry.date] = entry; });

    const availableWidth = container.clientWidth - 4;
    const barWidth = Math.max(Math.floor(availableWidth / 28) - 2, 2);
    let tooltipLeaveTimer;

    function getBarColorForStreak(streak) {
      if (!streak) return '#555555';
      if (streak >= 22) return '#FFD200';
      if (streak >= 15) return '#E4B800';
      if (streak >= 8) return '#C59A00';
      return '#A57C00';
    }

    dateList.forEach(dateStr => {
      const entry = entryMap[dateStr] || { date: dateStr, gold: 0, streak: 0, general: 0, role: 0 };
      const wrapper = document.createElement('div');
      wrapper.className = 'chart-bar-wrapper';
      wrapper.style.width = `${barWidth}px`;

      if (activeChartView === 'gold') {
        const barHeight = Math.max((entry.gold * GOLD_CHART_MULTIPLIER), 0);
        const bar = document.createElement('div');
        bar.className = 'chart-bar';
        if (entry.gold === 0) {
          bar.style.height = '0px';
          bar.style.backgroundColor = 'transparent';
        } else {
          bar.style.height = `${barHeight}px`;
          bar.style.backgroundColor = getBarColorForStreak(entry.streak);
        }
        wrapper.appendChild(bar);
      } else {
        wrapper.style.display = 'flex';
        wrapper.style.flexDirection = 'column';
        wrapper.style.justifyContent = 'space-between';
        wrapper.style.height = '100%';

        const usableHeight = 71;
        const stepHeight = usableHeight / 16;
        const generalCount = entry.general || 0;
        const roleCount = entry.role || 0;
        const bothCompleted = (generalCount === 7 && roleCount === 9);

        const topBar = document.createElement('div');
        topBar.className = 'chart-bar';
        topBar.style.borderRadius = '0 0 2px 2px';
        if (generalCount === 0) {
          topBar.style.height = '0px';
          topBar.style.backgroundColor = 'transparent';
        } else {
          topBar.style.height = `${generalCount * stepHeight}px`;
          topBar.style.backgroundColor = bothCompleted ? '#FFC107' : (generalCount === 7 ? '#999999' : '#E30000');
        }

        const bottomBar = document.createElement('div');
        bottomBar.className = 'chart-bar';
        bottomBar.style.borderRadius = '2px 2px 0 0';
        if (roleCount === 0) {
          bottomBar.style.height = '0px';
          bottomBar.style.backgroundColor = 'transparent';
        } else {
          bottomBar.style.height = `${roleCount * stepHeight}px`;
          bottomBar.style.backgroundColor = bothCompleted ? '#FFC107' : (roleCount === 9 ? '#999999' : '#E30000');
        }

        wrapper.appendChild(topBar);
        wrapper.appendChild(bottomBar);
      }

      container.appendChild(wrapper);
      const date = new Date(dateStr + 'T12:00:00Z');

      wrapper.addEventListener('mouseenter', () => {
        if (tooltipLeaveTimer) clearTimeout(tooltipLeaveTimer);
        const hasData = (activeChartView === 'gold') ? (entry.gold > 0) : ((entry.general || 0) > 0 || (entry.role || 0) > 0);

        if (hasData) {
          playHoverTick();
          wrapper.querySelectorAll('.chart-bar').forEach(seg => {
            if (seg.style.backgroundColor !== 'transparent') {
              seg.dataset.origBg = seg.style.backgroundColor;
              seg.style.backgroundColor = '#FFFFFF';
              seg.style.boxShadow = '0 0 8px rgba(255, 255, 255, 0.9)';
            }
          });
        }

        const humanDate = date.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
        const streakText = entry.streak ? `Day ${entry.streak} (Week ${Math.floor((entry.streak - 1) / 7) + 1})` : 'No Streak';
        let starChar = '☆';
        let starStyle = 'color: #444; opacity: 0.3; font-weight: normal;';

        if (entry.general === 7 && entry.role === 9) {
          starChar = '★';
          starStyle = 'color: #FFD700; text-shadow: 0 0 4px #FFD700, 0 0 10px #FFA500;';
        } else if (entry.general === 7 || entry.role === 9) {
          starChar = '★';
          starStyle = 'color: #C0C0C0; text-shadow: 0 0 3px rgba(192, 192, 192, 0.5);';
        }

        infoDisplay.innerHTML = `
          <div class="tooltip-top-row">
              <span class="tooltip-date">${humanDate}</span>
              <span class="tooltip-gold">${entry.gold.toFixed(2)} Gold</span>
              <span class="tooltip-star" style="${starStyle}">${starChar}</span>
          </div>
          <div class="tooltip-bottom-row">
              <span>Streak: ${streakText}</span>
              <span>Gen: ${entry.general}/7 | Role: ${entry.role}/9</span>
          </div>
        `;
        infoDisplay.style.color = '#aaa';
      });

      wrapper.addEventListener('mouseleave', () => {
        wrapper.querySelectorAll('.chart-bar').forEach(seg => {
          if (seg.dataset.origBg) {
            seg.style.backgroundColor = seg.dataset.origBg;
            seg.style.boxShadow = 'none';
          }
        });
        tooltipLeaveTimer = setTimeout(() => {
          infoDisplay.innerHTML = '&nbsp;';
        }, 200);
      });
    });
  }

  function validateStreakConsistency(currentStreak) {
    const lastCompletionDateStr = localStorage.getItem(LS_LAST_COMPLETION_DATE);
    const todayKey = getRDODayKey();
    if (!lastCompletionDateStr) {
      return (currentStreak > 0) ? 0 : currentStreak;
    }
    const diff = getDateDifferenceInDays(todayKey, lastCompletionDateStr);
    return (isNaN(diff) || diff > 1) ? 0 : currentStreak;
  }

  function loadStreak() {
    let currentStreak = parseInt(localStorage.getItem(LS_STREAK_COUNT) || '0', 10);
    if (isNaN(currentStreak)) currentStreak = 0;

    const validatedStreak = validateStreakConsistency(currentStreak);
    if (validatedStreak !== currentStreak) {
      currentStreak = validatedStreak;
      localStorage.setItem(LS_STREAK_COUNT, currentStreak);
      if (currentStreak === 0) {
        localStorage.removeItem(LS_LAST_COMPLETION_DATE);
        localStorage.removeItem(LS_CHALLENGE_STATUS);
      }
    }

    if (PYTHON_STREAK_OVERRIDE > -1) {
      currentStreak = PYTHON_STREAK_OVERRIDE;
      setStreakCount(currentStreak, true);
    }

    const lastCompletionDateStr = localStorage.getItem(LS_LAST_COMPLETION_DATE);
    const todayKey = getRDODayKey();
    if (lastCompletionDateStr) {
      const diff = getDateDifferenceInDays(todayKey, lastCompletionDateStr);
      if (diff === 1) {
        if (currentStreak >= MAX_RDO_STREAK) {
          currentStreak = 0;
          setStreakCount(0, false);
        } else {
          localStorage.removeItem(LS_CHALLENGE_STATUS);
        }
      }
    }

    localStorage.setItem(LS_STREAK_FOR_MULTIPLIER, currentStreak);
    const csEl = document.getElementById('current-streak');
    if (csEl) csEl.textContent = `${currentStreak} Days`;
  }

  function updateCounters() {
    const generalDone = Array.from(generalCheckboxes).filter(cb => cb.checked).length;
    const roleDone = Math.min(
      Array.from(roleCheckboxes).filter(cb => cb.checked && cb.closest('.role-challenge')?.style.display !== 'none').length,
      9
    );

    const gcEl = document.getElementById('general-counter');
    const rcEl = document.getElementById('role-counter');
    if (gcEl) {
      gcEl.textContent = `${generalDone}/7`;
      gcEl.classList.toggle('counter-glow', generalDone === 7);
    }
    if (rcEl) {
      rcEl.textContent = `${roleDone}/9`;
      rcEl.classList.toggle('counter-glow', roleDone === 9);
    }

    const dailyGoldTotal = calculateDailyGoldTotal(generalDone, roleDone);
    const currentStreak = parseInt(localStorage.getItem(LS_STREAK_COUNT) || '0', 10);

    const csEl = document.getElementById('current-streak');
    if (csEl) csEl.textContent = `${currentStreak} Days`;

    const goldDisplay = document.getElementById('daily-gold-total');
    const isDataCurrent = (getChallengeDateKey() === getRDODayKey());

    if (goldDisplay) {
      if (isDataCurrent) {
        logDailyGold(dailyGoldTotal, currentStreak, generalDone, roleDone);
        goldDisplay.innerHTML = formatGoldForDisplay(dailyGoldTotal);
      } else {
        goldDisplay.innerHTML = '<span style="color: #888; font-size: 0.8em;">PREVIOUS DAY DATA</span>';
      }
    }

    const sums = calculateLogSums(currentStreak);
    const cycleEl = document.getElementById('cycle-gold-total');
    const newCycleHTML = formatGoldForDisplay(sums.week);
    if (cycleEl && cycleEl.innerHTML !== newCycleHTML) {
      cycleEl.innerHTML = newCycleHTML;
      cycleEl.classList.remove('gold-exciting-flash');
      void cycleEl.offsetWidth;
      cycleEl.classList.add('gold-exciting-flash');
      setTimeout(() => cycleEl.classList.remove('gold-exciting-flash'), 1000);
    }

    const streakEl = document.getElementById('streak-gold-total');
    const newStreakHTML = formatGoldForDisplay(sums.running);
    if (streakEl && streakEl.innerHTML !== newStreakHTML) {
      streakEl.innerHTML = newStreakHTML;
      streakEl.classList.remove('gold-exciting-flash');
      void streakEl.offsetWidth;
      streakEl.classList.add('gold-exciting-flash');
      setTimeout(() => streakEl.classList.remove('gold-exciting-flash'), 1000);
    }

    const rolesContainer = document.getElementById('roles-container') || document.body;
    rolesContainer.classList.toggle('all-roles-completed', roleDone === 9);
    document.querySelectorAll('.difficulty-toggle').forEach(t => t.classList.toggle('dimmed-text', roleDone === 9));

    document.querySelectorAll('.role-container').forEach(rc => {
      const visible = Array.from(rc.querySelectorAll('.role-challenge')).filter(ch => ch.style.display !== 'none');
      const allComp = visible.length > 0 && visible.every(ch => ch.querySelector('.challenge-checkbox')?.checked);
      rc.querySelector('.role-heading')?.classList.toggle('dimmed', allComp);
    });

    renderGoldLogChart();
    debugGoldStats(dailyGoldTotal, sums.week, sums.running, JSON.parse(localStorage.getItem(LS_GOLD_LOG)) || []);
  }

  function handleStreakUpdate(isTicked) {
    const checkedCount = Array.from(allCheckboxes).filter(cb => cb.checked).length;
    const currentStatus = localStorage.getItem(LS_CHALLENGE_STATUS);
    const lockedStreak = parseInt(localStorage.getItem(LS_STREAK_FOR_MULTIPLIER) || '0', 10);

    if (isTicked && checkedCount > 0 && currentStatus !== 'completed') {
      setStreakCount(lockedStreak + 1, true);
    } else if (!isTicked && checkedCount === 0 && currentStatus === 'completed') {
      setStreakCount(lockedStreak, false);
    }
    updateCounters();
  }

  // Check storage expiry
  const dailyKeyCheck = localStorage.getItem(LS_LAST_KNOWN_TIMESTAMP);
  if (dailyKeyCheck != PYTHON_CHALLENGE_TIMESTAMP) {
    Object.keys(localStorage).forEach(k => {
      if (k.includes('_challenge_')) localStorage.removeItem(k);
    });
  }
  localStorage.setItem(LS_LAST_KNOWN_TIMESTAMP, PYTHON_CHALLENGE_TIMESTAMP);

  allCheckboxes.forEach(cb => {
    const key = `${PYTHON_CHALLENGE_TIMESTAMP}_${cb.id}`;
    cb.checked = localStorage.getItem(key) === "true";
    const wrapper = cb.closest('.challenge, .role-challenge');
    if (cb.checked && wrapper) wrapper.classList.add('completed');

    cb.addEventListener('change', () => {
      if (wrapper) wrapper.classList.toggle('completed', cb.checked);
      localStorage.setItem(key, cb.checked);
      handleStreakUpdate(cb.checked);
    });
  });

  const sUp = document.getElementById('streak-up');
  const sDown = document.getElementById('streak-down');
  if (sUp) {
    sUp.addEventListener('click', () => {
      localStorage.setItem(LS_STREAK_COUNT, Math.min(28, parseInt(localStorage.getItem(LS_STREAK_COUNT) || 0) + 1));
      localStorage.setItem(LS_STREAK_FOR_MULTIPLIER, localStorage.getItem(LS_STREAK_COUNT));
      updateCounters();
    });
  }
  if (sDown) {
    sDown.addEventListener('click', () => {
      localStorage.setItem(LS_STREAK_COUNT, Math.max(0, parseInt(localStorage.getItem(LS_STREAK_COUNT) || 0) - 1));
      localStorage.setItem(LS_STREAK_FOR_MULTIPLIER, localStorage.getItem(LS_STREAK_COUNT));
      updateCounters();
    });
  }

  document.querySelectorAll('.difficulty-toggle').forEach(toggle => {
    const roleContainer = toggle.closest('.role-container');
    const roleName = roleContainer.querySelector('.role-heading').textContent.split('(')[0].trim().toLowerCase().replace(/[^a-z0-9]/g, '');
    const lsKey = `difficulty_${roleName}`;

    function setView(diff) {
      roleContainer.querySelectorAll('.role-challenge').forEach(ch => {
        ch.style.display = (ch.dataset.difficulty === diff) ? '' : 'none';
      });
      toggle.dataset.difficulty = diff;
      if (diff === 'none') {
        toggle.textContent = '(Unpurchased)';
        toggle.style.color = '#777';
        toggle.style.fontStyle = 'italic';
      } else {
        toggle.style.color = '#dd0000';
        toggle.style.fontStyle = 'normal';
        const desc = diff === 'easy' ? 'Rank 1–5' : diff === 'med' ? 'Rank 6–14' : 'Rank 15+';
        const label = diff.charAt(0).toUpperCase() + diff.slice(1);
        toggle.textContent = `(${label}: ${desc})`;
      }
    }

    setView(localStorage.getItem(lsKey) || 'hard');

    toggle.addEventListener('click', () => {
      if (toggle.classList.contains('dimmed-text')) return;
      const current = toggle.dataset.difficulty;
      let next = 'easy';
      if (current === 'easy') next = 'med';
      else if (current === 'med') next = 'hard';
      else if (current === 'hard') next = 'none';
      else next = 'easy';

      localStorage.setItem(lsKey, next);
      setView(next);
      handleStreakUpdate(false);
    });
  });

  const viewToggle = document.getElementById('gold-log-heading');
  if (viewToggle) {
    viewToggle.addEventListener('click', () => {
      activeChartView = (activeChartView === 'gold') ? 'challenges' : 'gold';
      localStorage.setItem(LS_CHART_VIEW_MODE, activeChartView);
      viewToggle.textContent = (activeChartView === 'gold') ? "GOLD LOG (LAST 28 DAYS)" : "CHALLENGES (LAST 28 DAYS)";
      renderGoldLogChart();
    });
    viewToggle.textContent = (activeChartView === 'gold') ? "GOLD LOG (LAST 28 DAYS)" : "CHALLENGES (LAST 28 DAYS)";
  }

  loadStreak();
  updateCounters();
  window.addEventListener('load', renderGoldLogChart);
  window.addEventListener('resize', renderGoldLogChart);
});

// Pause button hook
document.addEventListener('DOMContentLoaded', () => {
  const pBtn = document.getElementById('pauseBtn');
  if (pBtn) {
    pBtn.addEventListener('click', () => {
      fetch('http://127.0.0.1:6969/pause', { method: 'POST' })
        .then(r => r.text()).then(d => alert(d)).catch(e => alert(e));
    });
  }
});