package server

import (
	"fmt"
	"log"
	"net/http"
	"time"
	"zfs-snapshot-manager/internal/config"
	"zfs-snapshot-manager/internal/handlers"
)

func StartServer(cfg *config.Config) {
	mux := http.NewServeMux()

	// Pass config to handlers
	mux.HandleFunc("/free", func(w http.ResponseWriter, r *http.Request) { handlers.FreeHandler(w, r, cfg) })
	mux.HandleFunc("/list", func(w http.ResponseWriter, r *http.Request) { handlers.ListHandler(w, r, cfg) })
	mux.HandleFunc("/create", func(w http.ResponseWriter, r *http.Request) { handlers.CreateHandler(w, r, cfg) })
	mux.HandleFunc("/delete", func(w http.ResponseWriter, r *http.Request) { handlers.DeleteHandler(w, r, cfg) })

	srv := &http.Server{
		Addr:         fmt.Sprintf(":%d", cfg.Port),
		Handler:      mux,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	log.Printf("Starting server on :%d\n", cfg.Port)
	if err := srv.ListenAndServe(); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
