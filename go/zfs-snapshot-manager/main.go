package main

import (
	"flag"
	"log"
	"zfs-snapshot-manager/internal/config"
	"zfs-snapshot-manager/internal/server"
)

func main() {
	// Get config file path from the first argument
	configPath := flag.String("config", "", "Path to YAML configuration file")
	flag.Parse()

	if *configPath == "" {
		log.Fatal("Usage: go run cmd/main.go --config <path-to-config.yaml>")
	}

	cfg, err := config.LoadConfig(*configPath)
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	log.Printf("Loaded config: %+v\n", cfg)

	server.StartServer(cfg)
}
