package config

import (
	"os"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Port             int      `yaml:"port"`
	AllowedDatasets  []string `yaml:"allowed_dataset_names"`
	AllowedSnapshots []string `yaml:"allowed_snapshot_names"`
}

func LoadConfig(filePath string) (*Config, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	var cfg Config
	err = yaml.Unmarshal(data, &cfg)
	if err != nil {
		return nil, err
	}

	return &cfg, nil
}
