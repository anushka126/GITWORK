# app.py - Main PySpotify Application
# Tkinter-based Spotify-like GUI (no audio playback)

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from data_manager import DataManager

# ─────────────────── COLOUR PALETTE ────────────────────────
BG_DARK    = "#0d0d0d"
BG_CARD    = "#1a1a1a"
BG_SIDEBAR = "#111111"
BG_PANEL   = "#161616"
ACCENT     = "#1DB954"       # Spotify green
ACCENT_HOV = "#1ed760"
TEXT_PRI   = "#FFFFFF"
TEXT_SEC   = "#b3b3b3"
TEXT_DIM   = "#535353"
RED_LIKE   = "#e91429"
GOLD       = "#f59b00"
BORDER     = "#282828"

FONT_TITLE   = ("Helvetica", 22, "bold")
FONT_HEADING = ("Helvetica", 14, "bold")
FONT_BODY    = ("Helvetica", 11)
FONT_SMALL   = ("Helvetica", 9)
FONT_MONO    = ("Courier", 10)


# ══════════════════════════════════════════════════════════
#  HELPER WIDGET – Scrollable Frame
# ══════════════════════════════════════════════════════════
class ScrollFrame(tk.Frame):
    """A frame with a vertical scrollbar."""
    def __init__(self, parent, bg=BG_PANEL, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = tk.Frame(canvas, bg=bg)
        self.inner.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        # Mouse wheel scrolling
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))


# ══════════════════════════════════════════════════════════
#  SONG ROW WIDGET
# ══════════════════════════════════════════════════════════
class SongRow(tk.Frame):
    """One clickable row representing a song."""

    def __init__(self, parent, song, index, on_select, on_like, is_liked, bg=BG_PANEL):
        super().__init__(parent, bg=bg, cursor="hand2")
        self.song = song
        self.bg = bg
        self._build(index, on_select, on_like, is_liked)
        # Hover effect
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))

    def _build(self, index, on_select, on_like, is_liked):
        # Index number
        tk.Label(self, text=str(index), width=3, anchor="e",
                 bg=self.bg, fg=TEXT_DIM, font=FONT_SMALL).pack(side="left", padx=(8,4))

        # Song info (title + artist)
        info_frame = tk.Frame(self, bg=self.bg)
        info_frame.pack(side="left", fill="x", expand=True, padx=6)
        tk.Label(info_frame, text=self.song.title, anchor="w",
                 bg=self.bg, fg=TEXT_PRI, font=("Helvetica", 11, "bold")).pack(anchor="w")
        tk.Label(info_frame, text=self.song.artist, anchor="w",
                 bg=self.bg, fg=TEXT_SEC, font=FONT_SMALL).pack(anchor="w")

        # Genre badge
        tk.Label(self, text=self.song.genre, width=12,
                 bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL,
                 relief="flat").pack(side="left", padx=8)

        # Duration
        tk.Label(self, text=self.song.duration, width=6,
                 bg=self.bg, fg=TEXT_DIM, font=FONT_SMALL).pack(side="left", padx=4)

        # Like button
        heart = "♥" if is_liked else "♡"
        color = RED_LIKE if is_liked else TEXT_DIM
        like_btn = tk.Label(self, text=heart, bg=self.bg, fg=color,
                            font=("Helvetica", 14), cursor="hand2")
        like_btn.pack(side="right", padx=10)
        like_btn.bind("<Button-1>", lambda e: on_like(self.song))

        # Select whole row
        self.bind("<Button-1>", lambda e: on_select(self.song))
        info_frame.bind("<Button-1>", lambda e: on_select(self.song))

        self.configure(pady=6)
        # Separator line
        sep = tk.Frame(self, height=1, bg=BORDER)
        sep.pack(fill="x", side="bottom")

    def _hover(self, entering):
        col = "#242424" if entering else self.bg
        self._set_bg(self, col)

    def _set_bg(self, widget, color):
        try:
            widget.configure(bg=color)
        except Exception:
            pass
        for child in widget.winfo_children():
            self._set_bg(child, color)


# ══════════════════════════════════════════════════════════
#  LOGIN / SIGNUP WINDOW
# ══════════════════════════════════════════════════════════
class AuthWindow(tk.Toplevel):
    def __init__(self, parent, dm, on_success):
        super().__init__(parent)
        self.dm = dm
        self.on_success = on_success
        self.title("PySpotify – Login")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.geometry("420x520")
        self._center()
        self._build()
        self.grab_set()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 420) // 2
        y = (self.winfo_screenheight() - 520) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        # Logo area
        logo_frame = tk.Frame(self, bg=BG_DARK)
        logo_frame.pack(pady=(40, 10))
        tk.Label(logo_frame, text="♫", font=("Helvetica", 48),
                 bg=BG_DARK, fg=ACCENT).pack()
        tk.Label(logo_frame, text="PySpotify", font=("Helvetica", 26, "bold"),
                 bg=BG_DARK, fg=TEXT_PRI).pack()
        tk.Label(logo_frame, text="Music is life. Discover yours.",
                 font=FONT_SMALL, bg=BG_DARK, fg=TEXT_SEC).pack(pady=4)

        # Tab buttons
        self.mode = tk.StringVar(value="login")
        tab_frame = tk.Frame(self, bg=BG_DARK)
        tab_frame.pack(pady=16)
        for text, val in [("Log In", "login"), ("Sign Up", "signup")]:
            b = tk.Button(tab_frame, text=text, width=10,
                          command=lambda v=val: self._switch_mode(v),
                          bg=ACCENT if val == "login" else BG_CARD,
                          fg=BG_DARK if val == "login" else TEXT_SEC,
                          font=("Helvetica", 11, "bold"),
                          relief="flat", cursor="hand2", pady=6)
            b.pack(side="left", padx=4)
            if val == "login":
                self.login_tab = b
            else:
                self.signup_tab = b

        # Form area
        form = tk.Frame(self, bg=BG_DARK)
        form.pack(padx=50, fill="x")

        tk.Label(form, text="Username", bg=BG_DARK, fg=TEXT_SEC,
                 font=FONT_SMALL, anchor="w").pack(fill="x")
        self.uname_entry = tk.Entry(form, bg=BG_CARD, fg=TEXT_PRI,
                                    insertbackground=TEXT_PRI, relief="flat",
                                    font=FONT_BODY)
        self.uname_entry.pack(fill="x", ipady=8, pady=(2, 12))

        tk.Label(form, text="Password", bg=BG_DARK, fg=TEXT_SEC,
                 font=FONT_SMALL, anchor="w").pack(fill="x")
        self.pwd_entry = tk.Entry(form, bg=BG_CARD, fg=TEXT_PRI,
                                   insertbackground=TEXT_PRI, relief="flat",
                                   font=FONT_BODY, show="●")
        self.pwd_entry.pack(fill="x", ipady=8, pady=(2, 20))

        self.action_btn = tk.Button(form, text="LOG IN", bg=ACCENT, fg=BG_DARK,
                                     font=("Helvetica", 12, "bold"), relief="flat",
                                     cursor="hand2", pady=10,
                                     command=self._submit)
        self.action_btn.pack(fill="x")

        self.msg_label = tk.Label(self, text="", bg=BG_DARK, fg=RED_LIKE, font=FONT_SMALL)
        self.msg_label.pack(pady=8)

        # Bind Enter key
        self.bind("<Return>", lambda e: self._submit())
        self.uname_entry.focus()

    def _switch_mode(self, mode):
        self.mode.set(mode)
        if mode == "login":
            self.login_tab.configure(bg=ACCENT, fg=BG_DARK)
            self.signup_tab.configure(bg=BG_CARD, fg=TEXT_SEC)
            self.action_btn.configure(text="LOG IN")
        else:
            self.signup_tab.configure(bg=ACCENT, fg=BG_DARK)
            self.login_tab.configure(bg=BG_CARD, fg=TEXT_SEC)
            self.action_btn.configure(text="SIGN UP")
        self.msg_label.configure(text="")

    def _submit(self):
        uname = self.uname_entry.get().strip()
        pwd = self.pwd_entry.get().strip()
        if self.mode.get() == "login":
            ok, result = self.dm.login_user(uname, pwd)
            if ok:
                self.destroy()
                self.on_success(result)
            else:
                self.msg_label.configure(text=result)
        else:
            ok, msg = self.dm.register_user(uname, pwd)
            if ok:
                self.msg_label.configure(text=msg, fg=ACCENT)
                self._switch_mode("login")
            else:
                self.msg_label.configure(text=msg, fg=RED_LIKE)


# ══════════════════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════════════════
class PySpotifyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PySpotify")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=BG_DARK)

        self.dm = DataManager()
        self.current_user = None
        self.current_song = None
        self.current_view = "home"  # active sidebar tab

        self._build_shell()
        self._show_auth()

    # ── Shell layout ──────────────────────────────────────
    def _build_shell(self):
        """Build the persistent app shell (sidebar + main area)."""
        # Top bar
        self.topbar = tk.Frame(self, bg=BG_SIDEBAR, height=54)
        self.topbar.pack(fill="x", side="top")
        self.topbar.pack_propagate(False)
        tk.Label(self.topbar, text="♫  PySpotify", font=("Helvetica", 16, "bold"),
                 bg=BG_SIDEBAR, fg=ACCENT).pack(side="left", padx=20, pady=10)
        self.user_label = tk.Label(self.topbar, text="", font=FONT_BODY,
                                    bg=BG_SIDEBAR, fg=TEXT_SEC)
        self.user_label.pack(side="right", padx=16)
        tk.Button(self.topbar, text="Logout", font=FONT_SMALL, bg=BG_CARD,
                  fg=TEXT_SEC, relief="flat", cursor="hand2",
                  command=self._logout).pack(side="right", padx=8, pady=10)

        # Body
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(body, bg=BG_SIDEBAR, width=190)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)

        # Main content
        self.main_area = tk.Frame(body, bg=BG_PANEL)
        self.main_area.pack(fill="both", expand=True, side="left")

        # Now playing bar
        self.nowplaying = tk.Frame(self, bg=BG_CARD, height=64)
        self.nowplaying.pack(fill="x", side="bottom")
        self.nowplaying.pack_propagate(False)
        self.np_label = tk.Label(self.nowplaying,
                                  text="Select a song to view its details",
                                  font=FONT_BODY, bg=BG_CARD, fg=TEXT_SEC)
        self.np_label.pack(side="left", padx=20, pady=12)
        self.np_details = tk.Label(self.nowplaying, text="",
                                    font=FONT_SMALL, bg=BG_CARD, fg=ACCENT)
        self.np_details.pack(side="right", padx=20)

        self._build_sidebar()

    def _build_sidebar(self):
        """Create navigation buttons in the sidebar."""
        nav_items = [
            ("🏠  Home",           "home"),
            ("🔍  Search",         "search"),
            ("❤️   Liked Songs",   "liked"),
            ("📋  Playlists",      "playlists"),
            ("📊  Analytics",      "analytics"),
            ("✨  Recommendations","recs"),
        ]
        tk.Label(self.sidebar, text="MENU", font=FONT_SMALL,
                 bg=BG_SIDEBAR, fg=TEXT_DIM).pack(anchor="w", padx=16, pady=(18, 6))

        self.nav_buttons = {}
        for label, view in nav_items:
            btn = tk.Button(self.sidebar, text=label, anchor="w",
                            font=("Helvetica", 11), relief="flat",
                            bg=BG_SIDEBAR, fg=TEXT_SEC, cursor="hand2",
                            padx=16, pady=8,
                            command=lambda v=view: self._navigate(v))
            btn.pack(fill="x")
            self.nav_buttons[view] = btn

    def _nav_highlight(self, view):
        """Highlight the active sidebar item."""
        for v, btn in self.nav_buttons.items():
            if v == view:
                btn.configure(bg="#282828", fg=TEXT_PRI, font=("Helvetica", 11, "bold"))
            else:
                btn.configure(bg=BG_SIDEBAR, fg=TEXT_SEC, font=("Helvetica", 11))

    # ── Auth ──────────────────────────────────────────────
    def _show_auth(self):
        self._clear_main()
        AuthWindow(self, self.dm, self._on_login)

    def _on_login(self, user):
        self.current_user = user
        self.user_label.configure(text=f"👤  {user.username}")
        self._navigate("home")

    def _logout(self):
        if self.current_user:
            self.dm.save_user(self.current_user)
        self.current_user = None
        self.current_song = None
        self.np_label.configure(text="Select a song to view its details")
        self.np_details.configure(text="")
        self.user_label.configure(text="")
        self._show_auth()

    # ── Navigation ────────────────────────────────────────
    def _navigate(self, view):
        if not self.current_user:
            return
        self.current_view = view
        self._nav_highlight(view)
        self._clear_main()
        views = {
            "home":      self._build_home,
            "search":    self._build_search,
            "liked":     self._build_liked,
            "playlists": self._build_playlists,
            "analytics": self._build_analytics,
            "recs":      self._build_recommendations,
        }
        views.get(view, self._build_home)()

    def _clear_main(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    # ── Song interaction ──────────────────────────────────
    def _select_song(self, song):
        """Handle song selection: update now-playing bar and analytics."""
        self.current_song = song
        self.dm.record_song_play(song.song_id)
        self.current_user.add_to_recently_played(song.song_id)
        self.dm.save_user(self.current_user)
        self.np_label.configure(
            text=f"♫  {song.title}  —  {song.artist}")
        self.np_details.configure(
            text=f"{song.genre}  |  {song.album}  |  {song.year}  |  {song.duration}")
        # Show song details popup
        self._song_detail_popup(song)

    def _song_detail_popup(self, song):
        """Popup window showing full song details."""
        win = tk.Toplevel(self)
        win.title("Song Details")
        win.configure(bg=BG_DARK)
        win.geometry("400x420")
        win.resizable(False, False)
        win.grab_set()

        # Center popup
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 420) // 2
        win.geometry(f"+{x}+{y}")

        # Header
        hdr = tk.Frame(win, bg=ACCENT, height=80)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="♫", font=("Helvetica", 40),
                 bg=ACCENT, fg=BG_DARK).pack(side="left", padx=20)
        title_frame = tk.Frame(hdr, bg=ACCENT)
        title_frame.pack(side="left")
        tk.Label(title_frame, text=song.title, font=("Helvetica", 15, "bold"),
                 bg=ACCENT, fg=BG_DARK).pack(anchor="w")
        tk.Label(title_frame, text=song.artist, font=FONT_BODY,
                 bg=ACCENT, fg=BG_DARK).pack(anchor="w")

        # Details
        body = tk.Frame(win, bg=BG_DARK, padx=28, pady=20)
        body.pack(fill="both", expand=True)
        details = [
            ("Album",    song.album),
            ("Genre",    song.genre),
            ("Year",     str(song.year)),
            ("Duration", song.duration),
            ("Plays",    str(song.play_count)),
        ]
        for label, value in details:
            row = tk.Frame(body, bg=BG_DARK)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, width=10, anchor="w",
                     font=("Helvetica", 10, "bold"), bg=BG_DARK, fg=TEXT_SEC).pack(side="left")
            tk.Label(row, text=value, anchor="w",
                     font=FONT_BODY, bg=BG_DARK, fg=TEXT_PRI).pack(side="left")
            tk.Frame(body, height=1, bg=BORDER).pack(fill="x")

        # Buttons row
        btn_row = tk.Frame(win, bg=BG_DARK, pady=12)
        btn_row.pack()

        is_liked = self.current_user.is_liked(song.song_id)
        like_text = "♥  Unlike" if is_liked else "♡  Like"
        like_col = RED_LIKE if is_liked else TEXT_SEC

        def toggle_like():
            liked = self.current_user.like_song(song.song_id)
            self.dm.save_user(self.current_user)
            new_text = "♥  Unlike" if liked else "♡  Like"
            new_col = RED_LIKE if liked else TEXT_SEC
            like_btn.configure(text=new_text, fg=new_col)

        like_btn = tk.Button(btn_row, text=like_text, fg=like_col,
                              font=FONT_BODY, bg=BG_CARD, relief="flat",
                              cursor="hand2", padx=14, pady=6, command=toggle_like)
        like_btn.pack(side="left", padx=6)

        def add_to_playlist_dialog():
            if not self.current_user.playlists:
                messagebox.showinfo("No Playlists",
                    "Create a playlist first from the Playlists section.", parent=win)
                return
            names = [p.name for p in self.current_user.playlists]
            dialog = PlaylistPickerDialog(win, names)
            self.wait_window(dialog)
            chosen = dialog.result
            if chosen:
                pl = self.current_user.get_playlist(chosen)
                if pl:
                    ok = pl.add_song(song.song_id)
                    self.dm.save_user(self.current_user)
                    msg = f"Added to '{chosen}'!" if ok else "Already in that playlist."
                    messagebox.showinfo("Playlist", msg, parent=win)

        tk.Button(btn_row, text="➕  Add to Playlist",
                  font=FONT_BODY, bg=BG_CARD, fg=TEXT_SEC, relief="flat",
                  cursor="hand2", padx=14, pady=6,
                  command=add_to_playlist_dialog).pack(side="left", padx=6)

        tk.Button(btn_row, text="Close", font=FONT_BODY,
                  bg=ACCENT, fg=BG_DARK, relief="flat",
                  cursor="hand2", padx=14, pady=6,
                  command=win.destroy).pack(side="left", padx=6)

    def _toggle_like(self, song):
        """Toggle like and refresh current view."""
        self.current_user.like_song(song.song_id)
        self.dm.save_user(self.current_user)
        self._navigate(self.current_view)

    # ── VIEW: Home ────────────────────────────────────────
    def _build_home(self):
        sf = ScrollFrame(self.main_area)
        sf.pack(fill="both", expand=True)
        inner = sf.inner

        # Welcome banner
        banner = tk.Frame(inner, bg="#1a2e1a")
        banner.pack(fill="x", padx=0, pady=0)
        tk.Label(banner, text=f"Welcome back, {self.current_user.username}! 👋",
                 font=("Helvetica", 20, "bold"), bg="#1a2e1a", fg=TEXT_PRI).pack(
                     anchor="w", padx=28, pady=(22, 4))
        tk.Label(banner, text="Here's your music universe.",
                 font=FONT_BODY, bg="#1a2e1a", fg=TEXT_SEC).pack(
                     anchor="w", padx=28, pady=(0, 18))

        songs = self.dm.get_all_songs()

        # Genre quick-filter row
        genres_frame = tk.Frame(inner, bg=BG_PANEL)
        genres_frame.pack(fill="x", padx=20, pady=12)
        tk.Label(genres_frame, text="Browse by Genre", font=FONT_HEADING,
                 bg=BG_PANEL, fg=TEXT_PRI).pack(anchor="w", pady=(0, 8))
        genre_row = tk.Frame(genres_frame, bg=BG_PANEL)
        genre_row.pack(anchor="w")
        genre_colors = [ACCENT, "#9b59b6", "#e74c3c", "#f39c12", "#1abc9c", "#3498db", "#e91429"]
        for i, genre in enumerate(self.dm.get_genres()):
            col = genre_colors[i % len(genre_colors)]
            def make_filter(g):
                return lambda: self._show_genre_songs(g)
            tk.Button(genre_row, text=genre, bg=col, fg=BG_DARK,
                      font=("Helvetica", 10, "bold"), relief="flat",
                      cursor="hand2", padx=12, pady=6,
                      command=make_filter(genre)).pack(side="left", padx=4)

        self._render_song_list(inner, songs, "All Songs")

    def _show_genre_songs(self, genre):
        self._clear_main()
        sf = ScrollFrame(self.main_area)
        sf.pack(fill="both", expand=True)
        songs = self.dm.get_songs_by_genre(genre)
        # Back button
        btn_row = tk.Frame(sf.inner, bg=BG_PANEL)
        btn_row.pack(anchor="w", padx=16, pady=8)
        tk.Button(btn_row, text="← Back", font=FONT_BODY, bg=BG_CARD, fg=TEXT_SEC,
                  relief="flat", cursor="hand2", padx=10, pady=4,
                  command=lambda: self._navigate("home")).pack(side="left")
        self._render_song_list(sf.inner, songs, f"{genre} Songs")

    # ── VIEW: Search ──────────────────────────────────────
    def _build_search(self):
        top = tk.Frame(self.main_area, bg=BG_PANEL)
        top.pack(fill="x", padx=24, pady=20)
        tk.Label(top, text="🔍  Search Songs", font=FONT_TITLE,
                 bg=BG_PANEL, fg=TEXT_PRI).pack(anchor="w")

        search_row = tk.Frame(self.main_area, bg=BG_PANEL)
        search_row.pack(fill="x", padx=24, pady=4)
        self.search_var = tk.StringVar()
        entry = tk.Entry(search_row, textvariable=self.search_var,
                         bg=BG_CARD, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                         font=("Helvetica", 13), relief="flat")
        entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        tk.Button(search_row, text="Search", bg=ACCENT, fg=BG_DARK,
                  font=("Helvetica", 11, "bold"), relief="flat",
                  cursor="hand2", padx=16, pady=8,
                  command=self._do_search).pack(side="left")
        entry.bind("<Return>", lambda e: self._do_search())
        entry.focus()

        self.results_area = tk.Frame(self.main_area, bg=BG_PANEL)
        self.results_area.pack(fill="both", expand=True)

    def _do_search(self):
        q = self.search_var.get().strip()
        for w in self.results_area.winfo_children():
            w.destroy()
        if not q:
            tk.Label(self.results_area, text="Type something to search.",
                     font=FONT_BODY, bg=BG_PANEL, fg=TEXT_DIM).pack(pady=30)
            return
        results = self.dm.search_songs(q)
        if not results:
            tk.Label(self.results_area, text=f'No results for "{q}".',
                     font=FONT_BODY, bg=BG_PANEL, fg=TEXT_DIM).pack(pady=30)
            return
        sf = ScrollFrame(self.results_area)
        sf.pack(fill="both", expand=True)
        tk.Label(sf.inner, text=f'{len(results)} result(s) for "{q}"',
                 font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SEC).pack(anchor="w", padx=16, pady=8)
        self._render_song_rows(sf.inner, results)

    # ── VIEW: Liked Songs ─────────────────────────────────
    def _build_liked(self):
        liked_ids = self.current_user.liked_song_ids
        liked_songs = list(filter(
            lambda s: s.song_id in liked_ids,
            self.dm.get_all_songs()
        ))
        sf = ScrollFrame(self.main_area)
        sf.pack(fill="both", expand=True)
        tk.Label(sf.inner, text="❤️  Liked Songs", font=FONT_TITLE,
                 bg=BG_PANEL, fg=TEXT_PRI).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(sf.inner, text=f"{len(liked_songs)} songs",
                 font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SEC).pack(anchor="w", padx=24)
        if liked_songs:
            self._render_song_rows(sf.inner, liked_songs)
        else:
            tk.Label(sf.inner, text="You haven't liked any songs yet.\nClick ♡ on any song to like it!",
                     font=FONT_BODY, bg=BG_PANEL, fg=TEXT_DIM, justify="center").pack(pady=50)

    # ── VIEW: Playlists ───────────────────────────────────
    def _build_playlists(self):
        frame = tk.Frame(self.main_area, bg=BG_PANEL)
        frame.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(frame, bg=BG_PANEL)
        hdr.pack(fill="x", padx=24, pady=(20, 10))
        tk.Label(hdr, text="📋  Playlists", font=FONT_TITLE,
                 bg=BG_PANEL, fg=TEXT_PRI).pack(side="left")
        tk.Button(hdr, text="+ New Playlist", bg=ACCENT, fg=BG_DARK,
                  font=("Helvetica", 11, "bold"), relief="flat",
                  cursor="hand2", padx=12, pady=6,
                  command=self._create_playlist).pack(side="right")

        playlists = self.current_user.playlists
        if not playlists:
            tk.Label(frame, text="No playlists yet.\nCreate one with the button above!",
                     font=FONT_BODY, bg=BG_PANEL, fg=TEXT_DIM, justify="center").pack(pady=50)
            return

        # Split: left = playlist list, right = playlist content
        pane = tk.Frame(frame, bg=BG_PANEL)
        pane.pack(fill="both", expand=True, padx=24)

        left = tk.Frame(pane, bg=BG_SIDEBAR, width=200)
        left.pack(fill="y", side="left")
        left.pack_propagate(False)

        right = tk.Frame(pane, bg=BG_PANEL)
        right.pack(fill="both", expand=True, side="left", padx=12)

        tk.Label(left, text="MY PLAYLISTS", font=FONT_SMALL,
                 bg=BG_SIDEBAR, fg=TEXT_DIM).pack(anchor="w", padx=10, pady=(10, 4))

        self.active_playlist_frame = right

        def show_playlist(pl):
            for w in right.winfo_children():
                w.destroy()
            self._render_playlist_detail(right, pl)

        for pl in playlists:
            row = tk.Frame(left, bg=BG_SIDEBAR, cursor="hand2")
            row.pack(fill="x")
            tk.Label(row, text=f"♪ {pl.name}", font=FONT_BODY,
                     bg=BG_SIDEBAR, fg=TEXT_PRI, anchor="w").pack(
                         side="left", padx=12, pady=7)
            tk.Label(row, text=str(len(pl.song_ids)), font=FONT_SMALL,
                     bg=BG_SIDEBAR, fg=TEXT_DIM).pack(side="right", padx=8)
            row.bind("<Button-1>", lambda e, p=pl: show_playlist(p))
            row.winfo_children()[0].bind("<Button-1>", lambda e, p=pl: show_playlist(p))
            tk.Frame(left, height=1, bg=BORDER).pack(fill="x")

        # Show first playlist by default
        show_playlist(playlists[0])

    def _render_playlist_detail(self, parent, pl):
        """Show songs inside a selected playlist."""
        hdr = tk.Frame(parent, bg=BG_PANEL)
        hdr.pack(fill="x", pady=(10, 6))
        tk.Label(hdr, text=f"♪  {pl.name}", font=FONT_HEADING,
                 bg=BG_PANEL, fg=TEXT_PRI).pack(side="left")
        tk.Label(hdr, text=f"Created {pl.created_at}  •  {len(pl.song_ids)} songs",
                 font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_DIM).pack(side="left", padx=12)
        tk.Button(hdr, text="🗑  Delete Playlist", font=FONT_SMALL,
                  bg=BG_CARD, fg=RED_LIKE, relief="flat", cursor="hand2",
                  command=lambda: self._delete_playlist(pl)).pack(side="right")

        songs = [self.dm.get_song(sid) for sid in pl.song_ids]
        songs = [s for s in songs if s]  # filter None

        if not songs:
            tk.Label(parent, text="This playlist is empty.\nAdd songs via the song detail popup.",
                     font=FONT_BODY, bg=BG_PANEL, fg=TEXT_DIM, justify="center").pack(pady=30)
            return

        sf = ScrollFrame(parent, bg=BG_PANEL)
        sf.pack(fill="both", expand=True)
        for i, song in enumerate(songs, 1):
            row = tk.Frame(sf.inner, bg=BG_PANEL, cursor="hand2")
            row.pack(fill="x")
            tk.Label(row, text=str(i), width=3, anchor="e",
                     bg=BG_PANEL, fg=TEXT_DIM, font=FONT_SMALL).pack(side="left", padx=6)
            info = tk.Frame(row, bg=BG_PANEL)
            info.pack(side="left", fill="x", expand=True, padx=6)
            tk.Label(info, text=song.title, anchor="w",
                     bg=BG_PANEL, fg=TEXT_PRI, font=("Helvetica", 11, "bold")).pack(anchor="w")
            tk.Label(info, text=song.artist, anchor="w",
                     bg=BG_PANEL, fg=TEXT_SEC, font=FONT_SMALL).pack(anchor="w")
            # Remove button
            def make_remove(s, p):
                return lambda: self._remove_from_playlist(s, p)
            tk.Button(row, text="✕", font=FONT_SMALL, bg=BG_PANEL, fg=RED_LIKE,
                      relief="flat", cursor="hand2",
                      command=make_remove(song, pl)).pack(side="right", padx=10)
            row.bind("<Button-1>", lambda e, s=song: self._select_song(s))
            tk.Frame(sf.inner, height=1, bg=BORDER).pack(fill="x")

    def _create_playlist(self):
        name = simpledialog.askstring("New Playlist", "Playlist name:",
                                      parent=self)
        if name:
            name = name.strip()
            pl = self.current_user.create_playlist(name)
            if pl:
                self.dm.save_user(self.current_user)
                self._navigate("playlists")
            else:
                messagebox.showerror("Error", "A playlist with that name already exists.")

    def _delete_playlist(self, pl):
        if messagebox.askyesno("Delete Playlist",
                               f"Delete '{pl.name}'? This cannot be undone."):
            self.current_user.delete_playlist(pl.name)
            self.dm.save_user(self.current_user)
            self._navigate("playlists")

    def _remove_from_playlist(self, song, pl):
        pl.remove_song(song.song_id)
        self.dm.save_user(self.current_user)
        self._navigate("playlists")

    # ── VIEW: Analytics ───────────────────────────────────
    def _build_analytics(self):
        sf = ScrollFrame(self.main_area)
        sf.pack(fill="both", expand=True)
        inner = sf.inner

        tk.Label(inner, text="📊  Analytics", font=FONT_TITLE,
                 bg=BG_PANEL, fg=TEXT_PRI).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(inner, text="Insights into the most popular songs and genres.",
                 font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SEC).pack(anchor="w", padx=24)

        # Top Songs
        self._analytics_section(inner, "🏆  Top 5 Most Played Songs",
                                 self._render_top_songs)
        # Top Genres
        self._analytics_section(inner, "🎵  Top Genres by Plays",
                                 self._render_top_genres)
        # Your recently played
        self._analytics_section(inner, "🕓  Your Recently Played",
                                 self._render_recently_played)

    def _analytics_section(self, parent, title, builder_fn):
        card = tk.Frame(parent, bg=BG_CARD, bd=0)
        card.pack(fill="x", padx=24, pady=10)
        tk.Label(card, text=title, font=FONT_HEADING,
                 bg=BG_CARD, fg=TEXT_PRI).pack(anchor="w", padx=16, pady=(14, 6))
        builder_fn(card)
        tk.Frame(card, height=8, bg=BG_CARD).pack()

    def _render_top_songs(self, parent):
        top = self.dm.get_top_songs(5)
        if not top:
            tk.Label(parent, text="No song plays recorded yet.",
                     font=FONT_BODY, bg=BG_CARD, fg=TEXT_DIM).pack(padx=16, pady=8)
            return
        max_plays = top[0][1] if top else 1
        for rank, (song, plays) in enumerate(top, 1):
            row = tk.Frame(parent, bg=BG_CARD)
            row.pack(fill="x", padx=16, pady=5)
            color = [GOLD, TEXT_SEC, "#cd7f32"][min(rank - 1, 2)] if rank <= 3 else TEXT_DIM
            tk.Label(row, text=f"#{rank}", width=3, font=("Helvetica", 11, "bold"),
                     bg=BG_CARD, fg=color).pack(side="left")
            info = tk.Frame(row, bg=BG_CARD)
            info.pack(side="left", fill="x", expand=True, padx=8)
            tk.Label(info, text=song.title, font=("Helvetica", 11, "bold"),
                     bg=BG_CARD, fg=TEXT_PRI, anchor="w").pack(anchor="w")
            tk.Label(info, text=f"{song.artist}  •  {song.genre}",
                     font=FONT_SMALL, bg=BG_CARD, fg=TEXT_SEC, anchor="w").pack(anchor="w")
            # Play bar
            pct = plays / max_plays
            bar_bg = tk.Frame(row, bg=BORDER, height=8, width=200)
            bar_bg.pack(side="right", padx=8)
            bar_bg.pack_propagate(False)
            bar_fill = tk.Frame(bar_bg, bg=ACCENT, height=8, width=int(200 * pct))
            bar_fill.place(x=0, y=0)
            tk.Label(row, text=f"{plays} plays", font=FONT_SMALL,
                     bg=BG_CARD, fg=TEXT_DIM, width=9, anchor="e").pack(side="right")

    def _render_top_genres(self, parent):
        genres = self.dm.get_top_genres(5)
        if not genres:
            tk.Label(parent, text="No plays recorded yet.",
                     font=FONT_BODY, bg=BG_CARD, fg=TEXT_DIM).pack(padx=16, pady=8)
            return
        max_plays = genres[0][1] if genres else 1
        colors = [ACCENT, "#9b59b6", "#e74c3c", "#f39c12", "#1abc9c"]
        for i, (genre, count) in enumerate(genres):
            row = tk.Frame(parent, bg=BG_CARD)
            row.pack(fill="x", padx=16, pady=5)
            tk.Label(row, text=genre, width=14, anchor="w",
                     font=("Helvetica", 11, "bold"), bg=BG_CARD,
                     fg=colors[i % len(colors)]).pack(side="left")
            pct = count / max_plays
            bar_bg = tk.Frame(row, bg=BORDER, height=12, width=250)
            bar_bg.pack(side="left", padx=8)
            bar_bg.pack_propagate(False)
            bar_fill = tk.Frame(bar_bg, bg=colors[i % len(colors)],
                                height=12, width=int(250 * pct))
            bar_fill.place(x=0, y=0)
            tk.Label(row, text=f"{count}", font=FONT_SMALL,
                     bg=BG_CARD, fg=TEXT_DIM).pack(side="left", padx=8)

    def _render_recently_played(self, parent):
        recent_ids = self.current_user.recently_played
        if not recent_ids:
            tk.Label(parent, text="No songs played yet.",
                     font=FONT_BODY, bg=BG_CARD, fg=TEXT_DIM).pack(padx=16, pady=8)
            return
        for i, sid in enumerate(recent_ids[:8], 1):
            song = self.dm.get_song(sid)
            if not song:
                continue
            row = tk.Frame(parent, bg=BG_CARD, cursor="hand2")
            row.pack(fill="x", padx=16, pady=3)
            tk.Label(row, text=str(i), width=3, anchor="e",
                     font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM).pack(side="left")
            tk.Label(row, text=f"{song.title}  —  {song.artist}",
                     font=FONT_BODY, bg=BG_CARD, fg=TEXT_PRI, anchor="w").pack(
                         side="left", padx=8)
            tk.Label(row, text=song.genre, font=FONT_SMALL,
                     bg=BG_CARD, fg=TEXT_SEC).pack(side="right", padx=8)
            row.bind("<Button-1>", lambda e, s=song: self._select_song(s))

    # ── VIEW: Recommendations ─────────────────────────────
    def _build_recommendations(self):
        sf = ScrollFrame(self.main_area)
        sf.pack(fill="both", expand=True)
        inner = sf.inner

        tk.Label(inner, text="✨  Recommended For You", font=FONT_TITLE,
                 bg=BG_PANEL, fg=TEXT_PRI).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(inner, text="Based on your listening history and popular songs.",
                 font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SEC).pack(anchor="w", padx=24, pady=(0, 12))

        recs = self.dm.get_recommendations(self.current_user, limit=10)
        if recs:
            self._render_song_rows(inner, recs)
        else:
            tk.Label(inner, text="Play some songs to get recommendations!",
                     font=FONT_BODY, bg=BG_PANEL, fg=TEXT_DIM).pack(pady=40)

    # ── Shared renderers ──────────────────────────────────
    def _render_song_list(self, parent, songs, heading):
        """Render a headed list of songs."""
        hdr = tk.Frame(parent, bg=BG_PANEL)
        hdr.pack(fill="x", padx=24, pady=(20, 6))
        tk.Label(hdr, text=heading, font=FONT_HEADING,
                 bg=BG_PANEL, fg=TEXT_PRI).pack(side="left")
        tk.Label(hdr, text=f"{len(songs)} songs",
                 font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_DIM).pack(side="left", padx=10)
        self._render_song_rows(parent, songs)

    def _render_song_rows(self, parent, songs):
        """Render SongRow widgets for a list of songs."""
        for i, song in enumerate(songs, 1):
            is_liked = self.current_user.is_liked(song.song_id)
            row = SongRow(parent, song, i,
                          on_select=self._select_song,
                          on_like=self._toggle_like,
                          is_liked=is_liked)
            row.pack(fill="x", padx=8)


# ══════════════════════════════════════════════════════════
#  PLAYLIST PICKER DIALOG
# ══════════════════════════════════════════════════════════
class PlaylistPickerDialog(tk.Toplevel):
    """Simple dialog to pick a playlist from a list."""

    def __init__(self, parent, playlist_names):
        super().__init__(parent)
        self.result = None
        self.title("Add to Playlist")
        self.configure(bg=BG_DARK)
        self.geometry("300x320")
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="Select a Playlist", font=FONT_HEADING,
                 bg=BG_DARK, fg=TEXT_PRI).pack(pady=(20, 10))

        listbox = tk.Listbox(self, bg=BG_CARD, fg=TEXT_PRI,
                              selectbackground=ACCENT, selectforeground=BG_DARK,
                              font=FONT_BODY, relief="flat", height=10)
        listbox.pack(fill="both", expand=True, padx=20)
        for name in playlist_names:
            listbox.insert(tk.END, name)

        def confirm():
            sel = listbox.curselection()
            if sel:
                self.result = playlist_names[sel[0]]
            self.destroy()

        tk.Button(self, text="Add", bg=ACCENT, fg=BG_DARK,
                  font=("Helvetica", 11, "bold"), relief="flat",
                  cursor="hand2", pady=8, command=confirm).pack(
                      fill="x", padx=20, pady=12)


# ══════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = PySpotifyApp()
    app.mainloop()
