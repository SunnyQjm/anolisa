/**
 * @license
 * Copyright 2025 Qwen Team
 * SPDX-License-Identifier: Apache-2.0
 */

import { describe, expect, it, vi } from 'vitest';
import {
  InputFormat,
  ToolConfirmationOutcome,
  type WaitingToolCall,
} from '@copilot-shell/core';
import { PermissionController } from './permissionController.js';
import type { IControlContext } from '../ControlContext.js';
import type { IPendingRequestRegistry } from './baseController.js';
import type { ControlResponse } from '../../types.js';

function createController(response: ControlResponse): PermissionController {
  const context = {
    config: {
      getInputFormat: () => InputFormat.STREAM_JSON,
      getDebugMode: () => false,
    },
    streamJson: { send: vi.fn() },
    sessionId: 'test-session',
    abortSignal: new AbortController().signal,
    debugMode: false,
    permissionMode: 'default',
    sdkMcpServers: new Set<string>(),
    mcpClients: new Map(),
    inputClosed: false,
  } as unknown as IControlContext;

  const registry = {
    registerIncomingRequest: vi.fn(),
    deregisterIncomingRequest: vi.fn(),
    registerOutgoingRequest: vi.fn(),
    deregisterOutgoingRequest: vi.fn(),
  } satisfies IPendingRequestRegistry;

  const controller = new PermissionController(
    context,
    registry,
    'PermissionController',
  );
  vi.spyOn(controller, 'sendControlRequest').mockResolvedValue(response);
  return controller;
}

function createWaitingToolCall(
  toolName: string,
  onConfirm: WaitingToolCall['confirmationDetails']['onConfirm'],
): WaitingToolCall {
  return {
    status: 'awaiting_approval',
    request: {
      callId: `call-${toolName}`,
      name: toolName,
      args: { command: 'df -h' },
      isClientInitiated: false,
      prompt_id: 'prompt-1',
    },
    confirmationDetails: {
      type: 'exec',
      title: 'Confirm Shell Command',
      command: 'df -h',
      rootCommand: 'df',
      onConfirm,
    },
  } as unknown as WaitingToolCall;
}

describe('PermissionController outgoing permissions', () => {
  it('passes host executed shell results to shell confirmations', async () => {
    const onConfirm = vi.fn().mockResolvedValue(undefined);
    const controller = createController({
      subtype: 'success',
      request_id: 'request-1',
      response: {
        behavior: 'host_executed_shell',
        result: {
          llmContent: 'command: df -h\nstatus: completed',
          returnDisplay: 'df -h completed',
        },
      },
    });

    controller.getToolCallUpdateCallback()([
      createWaitingToolCall('run_shell_command', onConfirm),
    ]);

    await vi.waitFor(() => {
      expect(onConfirm).toHaveBeenCalledWith(
        ToolConfirmationOutcome.ProceedOnce,
        {
          hostExecutedToolResult: {
            llmContent: 'command: df -h\nstatus: completed',
            returnDisplay: 'df -h completed',
          },
        },
      );
    });
  });

  it('rejects host executed shell results for non-shell tools', async () => {
    const onConfirm = vi.fn().mockResolvedValue(undefined);
    const controller = createController({
      subtype: 'success',
      request_id: 'request-1',
      response: {
        behavior: 'host_executed_shell',
        result: {
          llmContent: 'should not be accepted',
          returnDisplay: 'should not be accepted',
        },
      },
    });

    controller.getToolCallUpdateCallback()([
      createWaitingToolCall('write_file', onConfirm),
    ]);

    await vi.waitFor(() => {
      expect(onConfirm).toHaveBeenCalledWith(ToolConfirmationOutcome.Cancel, {
        cancelMessage:
          'host_executed_shell is only valid for shell tool requests',
      });
    });
  });

  it('rejects invalid host executed shell result payloads', async () => {
    const onConfirm = vi.fn().mockResolvedValue(undefined);
    const controller = createController({
      subtype: 'success',
      request_id: 'request-1',
      response: {
        behavior: 'host_executed_shell',
        result: { returnDisplay: 'missing llmContent' },
      },
    });

    controller.getToolCallUpdateCallback()([
      createWaitingToolCall('run_shell_command', onConfirm),
    ]);

    await vi.waitFor(() => {
      expect(onConfirm).toHaveBeenCalledWith(ToolConfirmationOutcome.Cancel, {
        cancelMessage: 'Invalid host_executed_shell result payload',
      });
    });
  });
});
