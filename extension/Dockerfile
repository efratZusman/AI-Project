FROM node:20-alpine

LABEL maintainer="ai-guard"
LABEL description="Chrome Extension build & verification container"

WORKDIR /app

# מעתיקים את קוד התוסף
COPY . .

# בדיקות מבנה בסיסיות
RUN test -f manifest.json

# בדיקות syntax לכל קבצי ה-JS בתוסף
RUN for file in *.js beforeSend/*.js chatMonitor/*.js; do \
      if [ -f "$file" ]; then \
        echo "Checking $file"; \
        node --check "$file"; \
      fi; \
    done

# אם הגענו עד כאן – התוסף תקין
CMD ["sh", "-c", "echo 'Chrome extension verified successfully'"]
