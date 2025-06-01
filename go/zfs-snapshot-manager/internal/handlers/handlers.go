package handlers

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"zfs-snapshot-manager/internal/config"
)

func respondWithJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

func validateRequest(w http.ResponseWriter, r *http.Request, cfg *config.Config, requireSnapshot bool) (string, string, bool) {
	dataset := r.URL.Query().Get("dataset")
	if dataset == "" {
		http.Error(w, "Missing dataset parameter", http.StatusBadRequest)
		return "", "", false
	}

	if !matchesAny(cfg.AllowedDatasets, dataset) {
		http.Error(w, "Dataset not allowed", http.StatusForbidden)
		return "", "", false
	}

	snapshot := r.URL.Query().Get("snapshot")
	if requireSnapshot {
		if snapshot == "" {
			http.Error(w, "Missing snapshot parameter", http.StatusBadRequest)
			return "", "", false
		}

		if !matchesAny(cfg.AllowedSnapshots, snapshot) {
			http.Error(w, "Snapshot not allowed", http.StatusForbidden)
			return "", "", false
		}
	}

	return dataset, snapshot, true
}

func matchesAny(patterns []string, value string) bool {
	for _, pattern := range patterns {
		if matched, _ := regexp.MatchString(pattern, value); matched {
			return true
		}
	}
	return false
}

func FreeHandler(w http.ResponseWriter, r *http.Request, cfg *config.Config) {
	dataset, _, valid := validateRequest(w, r, cfg, false)
	if !valid {
		return
	}

	cmd := exec.Command("zfs", "list", "-p", dataset)
	log.Printf("Running command: %s", cmd.String())
	output, err := cmd.CombinedOutput()
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to run zfs list: %v", err), http.StatusInternalServerError)
		return
	}

	lines := strings.Split(string(output), "\n")
	if len(lines) < 2 {
		http.Error(w, "Invalid zfs list output", http.StatusInternalServerError)
		return
	}

	fields := strings.Fields(lines[1])
	if len(fields) < 3 {
		http.Error(w, "Unexpected zfs list format", http.StatusInternalServerError)
		return
	}

	freeBytes, err := strconv.ParseInt(fields[2], 10, 64)
	if err != nil {
		http.Error(w, fmt.Sprintf("Unexpected value of free space '%s': %v'", fields[2], err), http.StatusInternalServerError)
	}
	free := fmt.Sprintf("%d", freeBytes/(1024*1024*1024))
	respondWithJSON(w, http.StatusOK, map[string]string{"free": free})
}

func ListHandler(w http.ResponseWriter, r *http.Request, cfg *config.Config) {
	dataset, _, valid := validateRequest(w, r, cfg, false)
	if !valid {
		return
	}

	cmd := exec.Command("zfs", "list", "-t", "snapshot", "-r", dataset)
	log.Printf("Running command: %s", cmd.String())
	output, err := cmd.CombinedOutput()
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to run zfs list: %v", err), http.StatusInternalServerError)
		return
	}

	lines := strings.Split(string(output), "\n")
	if len(lines) < 2 {
		http.Error(w, fmt.Sprintf("zfs list -t snapshot -r %v returned no results", dataset), http.StatusInternalServerError)
		return
	}

	snapshots := []map[string]string{}
	for _, line := range lines[1:] {
		fields := strings.Fields(line)
		if len(fields) < 4 {
			continue
		}

		if !strings.HasPrefix(fields[0], dataset+"@") {
			continue
		}

		snapshots = append(snapshots, map[string]string{
			"name":  strings.Split(fields[0], "@")[1],
			"used":  fields[1],
			"refer": fields[3],
		})
	}

	respondWithJSON(w, http.StatusOK, map[string]interface{}{"dataset": dataset, "snapshots": snapshots})
}

func CreateHandler(w http.ResponseWriter, r *http.Request, cfg *config.Config) {
	dataset, snapshot, valid := validateRequest(w, r, cfg, true)
	if !valid {
		return
	}

	cmd := exec.Command("zfs", "snapshot", fmt.Sprintf("%s@%s", dataset, snapshot))
	log.Printf("Running command: %s", cmd.String())
	if err := cmd.Run(); err != nil {
		http.Error(w, fmt.Sprintf("Failed to create snapshot: %v", err), http.StatusInternalServerError)
		return
	}

	respondWithJSON(w, http.StatusOK, map[string]string{"status": "success"})
}

func DeleteHandler(w http.ResponseWriter, r *http.Request, cfg *config.Config) {
	dataset, snapshot, valid := validateRequest(w, r, cfg, true)
	if !valid {
		return
	}

	cmd := exec.Command("zfs", "destroy", fmt.Sprintf("%s@%s", dataset, snapshot))
	log.Printf("Running command: %s", cmd.String())
	if err := cmd.Run(); err != nil {
		http.Error(w, fmt.Sprintf("Failed to delete snapshot: %v", err), http.StatusInternalServerError)
		return
	}

	respondWithJSON(w, http.StatusOK, map[string]string{"status": "success"})
}
