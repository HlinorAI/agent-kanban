/*
 * kanban-launcher — native launcher for the project kanban app.
 *
 * This is a compiled binary (not a shell script) ON PURPOSE: macOS TCC
 * attributes file access to app bundles with native executables and shows
 * the Documents-access prompt. Script-based .app bundles get silent
 * instant denials (no prompt, no entry in Files & Folders).
 *
 * Behavior (mirrors the previous bash launcher):
 *   kanban-launcher              open the dashboard (Chrome --app, fallback
 *                                to the default browser via /usr/bin/open),
 *                                then run the updater synchronously.
 *   kanban-launcher --update-only
 *                                no window; refresh facts only (used by the
 *                                scheduled LaunchAgent).
 *
 * Paths are baked in at compile time by install-macos.sh:
 *   -DUPDATER_PATH, -DHTML_PATH, optional -DCHROME_PATH, -DPYTHON_PATH
 *
 * Log: $HOME/Library/Logs/kanban-app.log (append).
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <errno.h>
#include <limits.h>
#include <spawn.h>
#include <sys/wait.h>

extern char **environ;

#ifndef UPDATER_PATH
#define UPDATER_PATH "/usr/local/lib/kanban-update.py"
#endif
#ifndef HTML_PATH
#define HTML_PATH "/usr/local/share/kanban.html"
#endif
#ifndef CHROME_PATH
#define CHROME_PATH "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
#endif
#ifndef PYTHON_PATH
#define PYTHON_PATH "/usr/bin/python3"
#endif
#define OPEN_PATH "/usr/bin/open"

static FILE *lg = NULL;

static void logmsg(const char *msg)
{
    FILE *out = lg ? lg : stderr;
    time_t t = time(NULL);
    struct tm tmv;
    char buf[40];

    localtime_r(&t, &tmv);
    strftime(buf, sizeof buf, "%Y-%m-%d %H:%M:%S", &tmv);
    fprintf(out, "[%s] %s\n", buf, msg);
    fflush(out);
}

static void logopen(void)
{
    const char *home = getenv("HOME");
    char path[PATH_MAX];

    if (!home)
        return;
    snprintf(path, sizeof path, "%s/Library/Logs/kanban-app.log", home);
    lg = fopen(path, "a");
}

static int spawn_with_log(char *const argv[], int wait_for)
{
    pid_t pid;
    posix_spawn_file_actions_t fa;
    int rc, st;

    posix_spawn_file_actions_init(&fa);
    if (lg) {
        int fd = fileno(lg);
        posix_spawn_file_actions_adddup2(&fa, fd, STDOUT_FILENO);
        posix_spawn_file_actions_adddup2(&fa, fd, STDERR_FILENO);
    }
    rc = posix_spawn(&pid, argv[0], &fa, NULL, argv, environ);
    posix_spawn_file_actions_destroy(&fa);
    if (rc != 0)
        return -1;
    if (!wait_for)
        return 0;
    if (waitpid(pid, &st, 0) < 0)
        return -1;
    return WIFEXITED(st) ? WEXITSTATUS(st) : 128;
}

int main(int argc, char **argv)
{
    char line[2 * PATH_MAX];
    int update_only = (argc > 1 && strcmp(argv[1], "--update-only") == 0);

    logopen();
    snprintf(line, sizeof line, "launch args: %s", update_only ? "--update-only" : "<none>");
    logmsg(line);

    if (!update_only) {
        if (access(CHROME_PATH, X_OK) == 0) {
            char apparg[PATH_MAX + 8];
            char *chrome_argv[] = { (char *)CHROME_PATH, apparg, NULL };

            snprintf(apparg, sizeof apparg, "--app=file://%s", HTML_PATH);
            if (spawn_with_log(chrome_argv, 0) == 0)
                logmsg("dashboard opened: Chrome --app");
            else
                logmsg("ERROR: chrome spawn failed");
        } else {
            char *open_argv[] = { (char *)OPEN_PATH, (char *)HTML_PATH, NULL };

            if (spawn_with_log(open_argv, 0) == 0)
                logmsg("dashboard opened: default browser");
            else
                logmsg("ERROR: open spawn failed");
        }
    }

    logmsg("updater started");
    {
        char *upd_argv[] = { (char *)PYTHON_PATH, (char *)UPDATER_PATH, (char *)HTML_PATH, NULL };
        int rc = spawn_with_log(upd_argv, 1);

        if (rc < 0) {
            logmsg("ERROR: updater spawn failed");
            return 1;
        }
        snprintf(line, sizeof line, "updater finished rc=%d", rc);
        logmsg(line);
        if (lg)
            fclose(lg);
        return rc;
    }
}
