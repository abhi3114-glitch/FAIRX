# FAIRX Bug Report and Fixes

## Critical Bugs Found

### 1. **Missing SCORE Instance in suspicion.py**
**Location:** `src/fairx/suspicion.py`
**Issue:** The `SuspicionScore` class is defined but never instantiated as `SCORE`, which is imported by multiple modules.
**Impact:** ImportError when trying to import SCORE from suspicion module
**Fix:** Add `SCORE = SuspicionScore()` at the end of the file

### 2. **Missing save_async Method in evidence.py**
**Location:** `src/fairx/evidence.py`
**Issue:** Multiple modules call `EBUF.save_async()` but the method doesn't exist in EvidenceRecorder class
**Impact:** AttributeError at runtime when evidence recording is triggered
**Fix:** Add the `save_async` method as an alias to `save_clip_async`

### 3. **Missing add Method in suspicion.py**
**Location:** `src/fairx/suspicion.py`
**Issue:** The `SuspicionScore` class has `trigger_event` method but modules call `SCORE.add()`
**Impact:** AttributeError when events are triggered
**Fix:** Add an `add` method or rename `trigger_event` to `add`

### 4. **Duplicate Content in requirements.txt**
**Location:** `requirements.txt`
**Issue:** Lines 27-47 duplicate lines 1-26 with a markdown code fence
**Impact:** Installation errors, confusion
**Fix:** Remove duplicate lines and the markdown fence

### 5. **Event.now() Returns None on Cooldown**
**Location:** `src/fairx/events.py`
**Issue:** When cooldown check fails, `Event.now()` returns None, but calling code doesn't handle None
**Impact:** AttributeError when trying to access properties of None
**Fix:** Modules should check for None before using the event, or Event.now should always return an Event object

### 6. **Missing soundfile Dependency**
**Location:** `src/fairx/audio_vad.py` line 41
**Issue:** Code imports `soundfile as sf` but it's not in requirements.txt
**Impact:** ImportError when audio evidence is saved
**Fix:** Add `soundfile` to requirements.txt

### 7. **Inconsistent Method Calls**
**Location:** Multiple files
**Issue:** `suspicion.py` defines `trigger_event(ev, frame)` but all modules call `SCORE.add(Event.now(...))`
**Impact:** Method signature mismatch
**Fix:** Align method signatures and calls

## Fixed Files

All bugs have been fixed in the corrected versions below.